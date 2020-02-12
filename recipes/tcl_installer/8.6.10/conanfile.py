from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os


class TclInstallerConan(ConanFile):
    name = "tcl_installer"
    version = "8.6.10"
    description = "Tcl is a very powerful but easy to learn dynamic programming language."
    topics = ("conan", "tcl", "scripting", "programming")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://tcl.tk"
    license = "TCL"
    settings = "os_build", "arch_build", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False]
    }
    default_options = {
        "fPIC": True,
        "shared": False,
    }
    _source_subfolder = "source_subfolder"
    requires = ("zlib/1.2.11")

    @property
    def _is_mingw_windows(self):
        return self.settings.os_build == "Windows" and self.settings.compiler == "gcc"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if self._is_mingw_windows and "CONAN_BASH_PATH" not in os.environ:
            self.build_requires("msys2/20161025")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "tcl" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _fix_sources(self):
        unix_config_dir = self._get_configure_dir("unix")
        # When disabling 64-bit support (in 32-bit), this test must be 0 in order to use "long long" for 64-bit ints
        # (${tcl_type_64bit} can be either "__int64" or "long long")
        tools.replace_in_file(os.path.join(unix_config_dir, "configure"),
                              "(sizeof(${tcl_type_64bit})==sizeof(long))",
                              "(sizeof(${tcl_type_64bit})!=sizeof(long))")

        unix_makefile_in = os.path.join(unix_config_dir, "Makefile.in")
        # Avoid building internal libraries as shared libraries
        tools.replace_in_file(unix_makefile_in, "--enable-shared --enable-threads", "--enable-threads")
        # Avoid clearing CFLAGS and LDFLAGS in the makefile
        tools.replace_in_file(unix_makefile_in, "\nCFLAGS\t", "\n#CFLAGS\t")
        tools.replace_in_file(unix_makefile_in, "\nLDFLAGS\t", "\n#LDFLAGS\t")
        # Use CFLAGS and CPPFLAGS as argument to CC
        tools.replace_in_file(unix_makefile_in, "${CFLAGS}", "${CFLAGS} ${CPPFLAGS}")
        # nmake creates a temporary file with mixed forward/backward slashes
        # force the filename to avoid cryptic error messages
        win_config_dir = self._get_configure_dir("win")
        win_makefile_vc = os.path.join(win_config_dir, "makefile.vc")
        tools.replace_in_file(win_makefile_vc, "@type << >$@", "type <<temp.tmp >$@")


    def config_options(self):
        if self.settings.os_build == "Windows":
            del self.options.fPIC

    def _get_default_build_system(self):
        if self.settings.os_build == "Macos":
            return "macosx"
        elif self.settings.os_build == "Linux":
            return "unix"
        elif self.settings.os_build == "Windows":
            return "win"
        else:
            raise ConanInvalidConfiguration("Unknown settings.os_build={}".format(self.settings.os))

    def _get_configure_dir(self, build_system=None):
        if build_system is None:
            build_system = self._get_default_build_system()
        if build_system not in ["win", "unix", "macosx"]:
            raise ConanInvalidConfiguration("Invalid build system: {}".format(build_system))
        return os.path.join(self.source_folder, self._source_subfolder, build_system)

    def _get_auto_tools(self):
        autoTools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        return autoTools

    def _build_nmake(self, targets):
        opts = []
        # https://core.tcl.tk/tips/doc/trunk/tip/477.md
        if not self.options.shared:
            opts.append("static")
        if self.settings.build_type == "Debug":
            opts.append("symbols")
        if "MD" in self.settings.compiler.runtime:
            opts.append("msvcrt")
        else:
            opts.append("nomsvcrt")
        if "d" not in self.settings.compiler.runtime:
            opts.append("unchecked")
        vcvars_command = tools.vcvars_command(self.settings)
        self.run(
            '{vcvars} && nmake -nologo -f "{cfgdir}/makefile.vc" INSTALLDIR="{pkgdir}" OPTS={opts} {targets}'.format(
                vcvars=vcvars_command,
                cfgdir=self._get_configure_dir("win"),
                pkgdir=self.package_folder,
                opts=",".join(opts),
                targets=" ".join(targets),
            ), cwd=self._get_configure_dir("win"),
        )

    def _build_autotools(self):
        conf_args = [
            "--enable-threads",
            "--enable-shared" if self.options.shared else "--disable-shared",
            "--enable-symbols" if self.settings.build_type == "Debug" else "--disable-symbols",
            "--enable-64bit" if self.settings.arch_build == "x86_64" else "--disable-64bit",
            "--prefix={}".format(self.package_folder),
        ]
        autoTools = self._get_auto_tools()
        autoTools.configure(configure_dir=self._get_configure_dir(), args=conf_args, vars={"PKG_CFG_ARGS": " ".join(conf_args)})

        # https://core.tcl.tk/tcl/tktview/840660e5a1
        for root, _, files in os.walk(self.build_folder):
            if "Makefile" in files:
                tools.replace_in_file(os.path.join(root, "Makefile"), "-Dstrtod=fixstrtod", "", strict=False)

        with tools.chdir(self.build_folder):
            autoTools.make()

    def build(self):
        self._fix_sources()
        if self.settings.compiler == "Visual Studio":
            # do not treat warnings as errors 
            tools.replace_in_file(os.path.join(self._source_subfolder, "win", "rules.vc"), "cwarn = $(cwarn) -WX", "")
            self._build_nmake(["release"])
        else:
            self._build_autotools()

    def package(self):
        if self.settings.compiler == "Visual Studio":
            self._build_nmake(["install-binaries", "install-libraries"])
            # there is no way to only install headers + libraries
            # hence why we build/install everything and then remove
        else:
            with tools.chdir(self.build_folder):
                autoTools = self._get_auto_tools()
                autoTools.make(target="install-binaries")
                autoTools.make(target="install-libraries")
                autoTools.make(target="install-msgs")
                autoTools.make(target="install-tzdata")
                autoTools.make(target="install-headers")
                autoTools.make(target="install-private-headers")
            pkgconfig_dir = os.path.join(self.package_folder, "lib", "pkgconfig")
            tools.rmdir(pkgconfig_dir)
        self.copy(pattern="license.terms", dst="licenses", src=self._source_subfolder)

        tclConfigShPath = os.path.join(self.package_folder, "lib", "tclConfig.sh")
        package_path = os.path.join(self.package_folder)
        if self._is_mingw_windows:
            package_path = package_path.replace("\\", "/")
        tools.replace_in_file(tclConfigShPath,
                              package_path,
                              "${TCL_ROOT}")
        tools.replace_in_file(tclConfigShPath,
                              "\nTCL_BUILD_",
                              "\n#TCL_BUILD_")

        tools.replace_in_file(tclConfigShPath,
                              "\nTCL_SRC_DIR",
                              "\n#TCL_SRC_DIR")

    def package_info(self):
        libdirs = []
        for root, _, _ in os.walk(os.path.join(self.package_folder, "lib"), topdown=False):
            newlibs = tools.collect_libs(self, root)
            if newlibs:
                libdirs.append(root)

        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.libdirs = libdirs
        self.cpp_info.includedirs = ["include"]

        tcl_library = os.path.join(self.package_folder, "lib", "{}{}".format(self.name, ".".join(self.version.split(".")[:2])))
        self.output.info("Setting TCL_LIBRARY environment variable to {}".format(tcl_library))
        self.env_info.TCL_LIBRARY = tcl_library

        tcl_root = self.package_folder
        self.output.info("Setting TCL_ROOT environment variable to {}".format(tcl_root))
        self.env_info.TCL_ROOT = tcl_root

        tclsh_list = list(filter(lambda fn: fn.startswith("tclsh"), os.listdir(os.path.join(self.package_folder, "bin"))))
        tclsh = os.path.join(self.package_folder, "bin", tclsh_list[0])
        self.output.info("Setting TCLSH environment variable to {}".format(tclsh))
        self.env_info.TCLSH = tclsh

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Adding PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
