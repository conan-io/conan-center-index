from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.files import apply_conandata_patches, chdir, collect_libs, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime, msvc_runtime_flag, NMakeToolchain
import os

required_conan_version = ">=1.54.0"


class TclConan(ConanFile):
    name = "tcl"
    description = "Tcl is a very powerful but easy to learn dynamic programming language."
    license = "TCL"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://tcl.tk"
    topics = ("tcl", "scripting", "programming")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        # Not using basic_layout because package() needs the source folder to be a sub-directory of the build folder
        self.folders.source = "src"
        self.folders.generators = "conan"

    def requirements(self):
        self.requires("zlib/1.2.13")

    def validate(self):
        if self.settings.os not in ("FreeBSD", "Linux", "Macos", "Windows"):
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on {self.settings.os}.")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not is_msvc(self):
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = NMakeToolchain(self)
            tc.generate()
        else:
            tc = AutotoolsToolchain(self, prefix=self.package_folder)
            def yes_no(v): return "yes" if v else "no"
            tc.configure_args.extend([
                "--enable-threads",
                "--enable-symbols={}".format(yes_no(self.settings.build_type == "Debug")),
                "--enable-64bit={}".format(yes_no(self.settings.arch == "x86_64")),
            ])
            tc.generate()

    def _get_default_build_system_subdir(self):
        return {
            "Macos": "macosx",
            "Linux": "unix",
            "Windows": "win",
        }[str(self.settings.os)]

    def _get_configure_dir(self, build_system_subdir=None):
        if build_system_subdir is None:
            build_system_subdir = self._get_default_build_system_subdir()
        return os.path.join(self.source_folder, build_system_subdir)

    def _patch_sources(self):
        apply_conandata_patches(self)

        if is_apple_os(self) and self.settings.arch not in ("x86", "x86_64"):
            replace_in_file(self, os.path.join(self._get_configure_dir(), "configure"), "#define HAVE_CPUID 1", "#undef HAVE_CPUID")

        unix_config_dir = self._get_configure_dir("unix")
        # When disabling 64-bit support (in 32-bit), this test must be 0 in order to use "long long" for 64-bit ints
        # (${tcl_type_64bit} can be either "__int64" or "long long")
        replace_in_file(self, os.path.join(unix_config_dir, "configure"),
                        "(sizeof(${tcl_type_64bit})==sizeof(long))",
                        "(sizeof(${tcl_type_64bit})!=sizeof(long))")

        unix_makefile_in = os.path.join(unix_config_dir, "Makefile.in")
        # Avoid building internal libraries as shared libraries
        replace_in_file(self, unix_makefile_in, "--enable-shared --enable-threads", "--enable-threads")
        # Avoid clearing CFLAGS and LDFLAGS in the makefile
        replace_in_file(self, unix_makefile_in, "\nCFLAGS\t", "\n#CFLAGS\t")
        replace_in_file(self, unix_makefile_in, "\nLDFLAGS\t", "\n#LDFLAGS\t")
        # Use CFLAGS and CPPFLAGS as argument to CC
        replace_in_file(self, unix_makefile_in, "${CFLAGS}", "${CFLAGS} ${CPPFLAGS}")
        # nmake creates a temporary file with mixed forward/backward slashes
        # force the filename to avoid cryptic error messages
        win_config_dir = self._get_configure_dir("win")
        win_makefile_vc = os.path.join(win_config_dir, "makefile.vc")
        replace_in_file(self, win_makefile_vc, "@type << >$@", "type <<temp.tmp >$@")

        win_rules_vc = os.path.join(self.source_folder, "win", "rules.vc")
        # do not treat nmake build warnings as errors
        replace_in_file(self, win_rules_vc, "cwarn = $(cwarn) -WX", "")
        # disable whole program optimization to be portable across different MSVC versions.
        # See conan-io/conan-center-index#4811 conan-io/conan-center-index#4094
        replace_in_file(self,
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
        if is_msvc_static_runtime(self):
            opts.append("nomsvcrt")
        else:
            opts.append("msvcrt")
        if "d" not in msvc_runtime_flag(self):
            opts.append("unchecked")

        with chdir(self, self._get_configure_dir("win")):
            self.run('nmake -nologo -f "{cfgdir}/makefile.vc" INSTALLDIR="{pkgdir}" OPTS={opts} {targets}'.format(
                cfgdir=self._get_configure_dir("win"),
                pkgdir=self.package_folder,
                opts=",".join(opts),
                targets=" ".join(targets),
            ))

    def build(self):
        self._patch_sources()
        if is_msvc(self):
            self._build_nmake(["release"])
        else:
            autotools = Autotools(self)
            autotools.configure(self._get_configure_dir())

            # https://core.tcl.tk/tcl/tktview/840660e5a1
            for root, _, list_of_files in os.walk(self.build_folder):
                if "Makefile" in list_of_files:
                    replace_in_file(self, os.path.join(root, "Makefile"), "-Dstrtod=fixstrtod", "", strict=False)

    def package(self):
        copy(self, "license.terms", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            self._build_nmake(["install-binaries", "install-libraries"])
        else:
            autotools = Autotools(self)
            autotools.make(target="install")
            autotools.make(target="install-private-headers")

            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "man"))
            rmdir(self, os.path.join(self.package_folder, "share"))

        tclConfigShPath = os.path.join(self.package_folder, "lib", "tclConfig.sh")
        package_path = self.package_folder
        build_folder = self.build_folder
        if self.settings.os == "Windows" and not is_msvc(self):
            package_path = package_path.replace("\\", "/")
            drive, path = os.path.splitdrive(self.build_folder)
            build_folder = "".join([drive, path.lower().replace("\\", "/")])

        replace_in_file(self, tclConfigShPath,
                        package_path,
                        "${TCL_ROOT}")
        replace_in_file(self, tclConfigShPath,
                        build_folder,
                        "${TCL_BUILD_ROOT}")

        replace_in_file(self, tclConfigShPath,
                        "\nTCL_BUILD_",
                        "\n#TCL_BUILD_")
        replace_in_file(self, tclConfigShPath,
                        "\nTCL_SRC_DIR",
                        "\n#TCL_SRC_DIR")

        #fix_apple_shared_install_name(self)

    def package_info(self):
        libs = []
        systemlibs = []
        libdirs = []
        for root, _, _ in os.walk(os.path.join(self.package_folder, "lib"), topdown=False):
            newlibs = collect_libs(self, root)
            if newlibs:
                libs.extend(newlibs)
                libdirs.append(root)
        if self.settings.os == "Windows":
            systemlibs.extend(["ws2_32", "netapi32", "userenv"])
        elif self.settings.os in ("FreeBSD", "Linux"):
            systemlibs.extend(["dl", "m", "pthread"])

        defines = []
        if not self.options.shared:
            defines.append("STATIC_BUILD")
        self.cpp_info.defines = defines

        self.cpp_info.libdirs = libdirs
        self.cpp_info.libs = libs
        self.cpp_info.system_libs = systemlibs
        self.cpp_info.set_property("cmake_file_name", "TCL")
        self.cpp_info.names["cmake_find_package"] = "TCL"
        self.cpp_info.names["cmake_find_package_multi"] = "TCL"

        if self.settings.os == "Macos":
            self.cpp_info.frameworks = ["CoreFoundation"]
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags

        tcl_library = os.path.join(self.package_folder, "lib", "{}{}".format(self.name, ".".join(self.version.split(".")[:2])))
        self.output.info("Setting TCL_LIBRARY environment variable to {}".format(tcl_library))
        self.runenv_info.define_path('TCL_LIBRARY', tcl_library)
        self.env_info.TCL_LIBRARY = tcl_library

        tcl_root = self.package_folder
        self.output.info("Setting TCL_ROOT environment variable to {}".format(tcl_root))
        self.runenv_info.define_path('TCL_ROOT', tcl_root)
        self.env_info.TCL_ROOT = tcl_root

        tclsh_list = list(filter(lambda fn: fn.startswith("tclsh"), os.listdir(os.path.join(self.package_folder, "bin"))))
        tclsh = os.path.join(self.package_folder, "bin", tclsh_list[0])
        self.output.info("Setting TCLSH environment variable to {}".format(tclsh))
        self.runenv_info.define_path('TCLSH', tclsh)
        self.env_info.TCLSH = tclsh

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Adding PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
