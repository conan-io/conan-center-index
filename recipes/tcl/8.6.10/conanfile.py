from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os


class TclConan(ConanFile):
    name = "tcl"
    version = "8.6.10"
    description = "Tcl is a very powerful but easy to learn dynamic programming language."
    topics = ("conan", "tcl", "scripting", "programming")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://tcl.tk"
    license = "TCL"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "fPIC": [True, False],
        "shared": [True, False]
    }
    default_options = {
        "fPIC": True,
        "shared": False,
    }
    exports_sources = ("patches/*")
    requires = ("zlib/1.2.11")

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.os not in ("Linux", "Macos", "Windows"):
            raise ConanInvalidConfiguration("Unsupported os")
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if tools.os_info.is_windows and self.settings.compiler != "Visual Studio" and \
                "CONAN_BASH_PATH" not in os.environ and tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _get_default_build_system_subdir(self):
            return {
                "Macos": "macosx",
                "Linux": "unix",
                "Windows": "win",
            }[str(self.settings.os)]

    def _get_configure_dir(self, build_system_subdir=None):
        if build_system_subdir is None:
            build_system_subdir = self._get_default_build_system_subdir()
        return os.path.join(self.source_folder, self._source_subfolder, build_system_subdir)

    def _patch_sources(self):
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

        win_rules_vc = os.path.join(self._source_subfolder, "win", "rules.vc")
        # do not treat nmake build warnings as errors
        tools.replace_in_file(win_rules_vc, "cwarn = $(cwarn) -WX", "")
        # disable whole program optimization to be portable across different MSVC versions.
        # See conan-io/conan-center-index#4811 conan-io/conan-center-index#4094
        tools.replace_in_file(
            win_rules_vc,
            "OPTIMIZATIONS  = $(OPTIMIZATIONS) -GL",
            "")

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
        with tools.vcvars(self.settings):
            with tools.chdir(self._get_configure_dir("win")):
                self.run('nmake -nologo -f "{cfgdir}/makefile.vc" INSTALLDIR="{pkgdir}" OPTS={opts} {targets}'.format(
                    cfgdir=self._get_configure_dir("win"),
                    pkgdir=self.package_folder,
                    opts=",".join(opts),
                    targets=" ".join(targets),
                ))

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_args = [
            "--enable-threads",
            "--enable-shared" if self.options.shared else "--disable-shared",
            "--enable-symbols" if self.settings.build_type == "Debug" else "--disable-symbols",
            "--enable-64bit" if self.settings.arch == "x86_64" else "--disable-64bit",
        ]
        self._autotools.configure(configure_dir=self._get_configure_dir(), args=conf_args, vars={"PKG_CFG_ARGS": " ".join(conf_args)})

        # https://core.tcl.tk/tcl/tktview/840660e5a1
        for root, _, files in os.walk(self.build_folder):
            if "Makefile" in files:
                tools.replace_in_file(os.path.join(root, "Makefile"), "-Dstrtod=fixstrtod", "", strict=False)
        return self._autotools

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        self._patch_sources()
        if self.settings.compiler == "Visual Studio":
            self._build_nmake(["release"])
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="license.terms", dst="licenses", src=self._source_subfolder)
        if self.settings.compiler == "Visual Studio":
            self._build_nmake(["install-binaries", "install-libraries"])
        else:
            autotools = self._configure_autotools()
            autotools.install()
            autotools.make(target="install-private-headers")

            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.rmdir(os.path.join(self.package_folder, "man"))
            tools.rmdir(os.path.join(self.package_folder, "share"))

        tclConfigShPath = os.path.join(self.package_folder, "lib", "tclConfig.sh")
        package_path = self.package_folder
        build_folder = self.build_folder
        if self.settings.os == "Windows" and self.settings.compiler != "Visual Studio":
            package_path = package_path.replace("\\", "/")
            drive, path = os.path.splitdrive(self.build_folder)
            build_folder = "".join([drive, path.lower().replace("\\", "/")])

        tools.replace_in_file(tclConfigShPath,
                              package_path,
                              "${TCL_ROOT}")
        tools.replace_in_file(tclConfigShPath,
                              build_folder,
                              "${TCL_BUILD_ROOT}")

        tools.replace_in_file(tclConfigShPath,
                              "\nTCL_BUILD_",
                              "\n#TCL_BUILD_")
        tools.replace_in_file(tclConfigShPath,
                              "\nTCL_SRC_DIR",
                              "\n#TCL_SRC_DIR")

    def package_info(self):
        libs = []
        systemlibs = []
        libdirs = []
        for root, _, _ in os.walk(os.path.join(self.package_folder, "lib"), topdown=False):
            newlibs = tools.collect_libs(self, root)
            if newlibs:
                libs.extend(newlibs)
                libdirs.append(root)
        if self.settings.os == "Windows":
            systemlibs.extend(["ws2_32", "netapi32", "userenv"])
        else:
            systemlibs.extend(["m", "pthread", "dl"])

        defines = []
        if not self.options.shared:
            defines.append("STATIC_BUILD")
        self.cpp_info.defines = defines

        self.cpp_info.libdirs = libdirs
        self.cpp_info.libs = libs
        self.cpp_info.system_libs = systemlibs
        self.cpp_info.names["cmake_find_package"] = "TCL"
        self.cpp_info.names["cmake_find_package_multi"] = "TCL"

        if self.settings.os == "Macos":
            self.cpp_info.frameworks = ["Cocoa"]
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags

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
