from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, get, replace_in_file, rmdir, collect_libs
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path, msvc_runtime_flag, VCVars
from conan.tools.scm import Version

required_conan_version = ">=1.51.3"


class TclConan(ConanFile):
    name = "tcl"
    description = "Tcl is a very powerful but easy to learn dynamic programming language."
    license = "TCL"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://tcl.tk"
    topics = ("tcl", "scripting", "programming")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
    }

    @property
    def _settings_build(self):
        # TODO: Remove for Conan v2
        return getattr(self, "settings_build", self.settings)

    @property
    def win_bash(self):
        return self._settings_build.os == "Windows" and not is_msvc(self)

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except ValueError:
                pass
        try:
            del self.settings.compiler.libcxx  # for plain C projects only
        except ValueError:
            pass
        try:
            del self.settings.compiler.cppstd  # for plain C projects only
        except ValueError:
            pass

    def layout(self):
        basic_layout(self, src_folder="tcl")

    def requirements(self):
        # When compiled with msvc it would currently use the zlib provided in compat directory
        if not is_msvc(self):
            self.requires("zlib/1.2.12")

    def validate(self):
        if is_msvc(self) and self.options.shared != ("MD" in msvc_runtime_flag(self)):
            raise ConanInvalidConfiguration(f"compiler.runtime = {self.settings.get_safe('compiler.runtime')} while tcl:shared = {self.options.shared}")
        if self.settings.os not in ("FreeBSD", "Linux", "Macos", "Windows"):
            raise ConanInvalidConfiguration("Unsupported os")

    def build_requirements(self):
        if self.win_bash and not self.conf.get("tools.microsoft.bash:path", default=False, check_type=bool):
            self.tool_requires("msys2/cci.latest")
        if not is_msvc(self):
            self.tool_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def _get_default_build_system_subdir(self):
        return {
            "Macos": "macosx",
            "Linux": "unix",
            "Windows": "win",
        }[str(self.settings.os)]

    def _get_configure_dir(self, build_system_subdir=None):
        if build_system_subdir is None:
            build_system_subdir = self._get_default_build_system_subdir()
        return self.source_path.joinpath(build_system_subdir)

    def generate(self):
        if not is_msvc(self):
            tc = AutotoolsToolchain(self)
            yes_no = lambda v: "yes" if v else "no"

            # The default Autotools configuration flags are not used by Tcl
            tc.configure_args = tc._default_configure_install_flags() + [
                "--datadir=${prefix}/res",
                "--enable-threads",
                "--enable-shared={}".format(yes_no(self.options.shared)),
                "--enable-symbols={}".format(yes_no(self.settings.build_type == "Debug")),
                "--enable-64bit={}".format(yes_no(self.settings.arch == "x86_64")),
            ]
            tc.generate()

            deps = AutotoolsDeps(self)
            if self._settings_build.os == "Windows":
                deps_env = deps.environment
                # Workaround for: https://github.com/conan-io/conan/issues/11922
                ldflags = [f"-L{unix_path(self, lib[9:])} " if lib.startswith("/LIBPATH:") else f"{lib} " for lib in deps_env.vars(self)["LDFLAGS"].split(" ")]
                cppflags = [f"-I{unix_path(self, lib[2:])} " if lib.startswith("/I") else f"{lib} " for lib in deps_env.vars(self)["CPPFLAGS"].split(" ")]
                deps_env.define("LDFLAGS", ldflags)
                deps_env.define("CPPFLAGS", cppflags)
            deps.generate()
        else:
            if self._settings_build.os == "Windows":
                vcvars = VCVars(self)
                vcvars.generate(scope="build")

            deps = AutotoolsDeps(self)
            deps.generate(scope="build")

        vb = VirtualBuildEnv(self)
        if not is_msvc(self):
            pkg_env = vb.environment()
            pkg_env.define("PKG_CFG_ARGS", " ".join(tc.configure_args))
            pkg_vars = pkg_env.vars(self, scope="build")
            pkg_vars.save_script("pkg_vars")
        vb.generate(scope="build")

    def _patch_sources(self):
        apply_conandata_patches(self)

        if is_apple_os(self) and self.settings.arch not in ("x86", "x86_64"):
            replace_in_file(self, self._get_configure_dir().joinpath("configure"), "#define HAVE_CPUID 1", "#undef HAVE_CPUID")

        unix_config_dir = self._get_configure_dir("unix")
        # When disabling 64-bit support (in 32-bit), this test must be 0 in order to use "long long" for 64-bit ints
        # (${tcl_type_64bit} can be either "__int64" or "long long")
        replace_in_file(self, unix_config_dir.joinpath("configure"), "(sizeof(${tcl_type_64bit})==sizeof(long))", "(sizeof(${tcl_type_64bit})!=sizeof(long))")

        unix_makefile_in = unix_config_dir.joinpath("Makefile.in")
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
        win_makefile_vc = win_config_dir.joinpath("makefile.vc")
        replace_in_file(self, win_makefile_vc, "@type << >$@", "type <<temp.tmp >$@")

        win_rules_vc = self.source_path.joinpath("win", "rules.vc")
        # do not treat nmake build warnings as errors
        replace_in_file(self, win_rules_vc, "cwarn = $(cwarn) -WX", "")
        # disable whole program optimization to be portable across different MSVC versions.
        # See conan-io/conan-center-index#4811 conan-io/conan-center-index#4094
        replace_in_file(self, win_rules_vc, "OPTIMIZATIONS  = $(OPTIMIZATIONS) -GL", "")

    def build(self):
        self._patch_sources()

        if is_msvc(self):
            opts = []
            # https://core.tcl.tk/tips/doc/trunk/tip/477.md
            if not self.options.shared:
                opts.append("static")
            if self.settings.build_type == "Debug":
                opts.append("symbols")
            if "MD" in msvc_runtime_flag(self):
                opts.append("msvcrt")
            else:
                opts.append("nomsvcrt")
            if "d" not in msvc_runtime_flag(self):
                opts.append("unchecked")
            opts_arg = ",".join(opts)
            self.run(f'nmake -nologo -f "{self._get_configure_dir().joinpath("makefile.vc")}" INSTALLDIR="{self.package_path}" OPTS={opts_arg} {str(self.settings.build_type).lower()}',
                     cwd=self._get_configure_dir())
        else:
            autotools = Autotools(self)
            autotools.configure(build_script_folder=self._get_configure_dir())
            autotools.make()

            # https://core.tcl.tk/tcl/tktview/840660e5a1
            for makefile in self.build_path.glob("**/Makefile*"):
                replace_in_file(self, makefile, "-Dstrtod=fixstrtod", "", strict=False)

    def package(self):
        copy(self, "license.terms", src=self.source_folder, dst=self.package_path.joinpath("licenses"))

        if is_msvc(self):
            self.run(f'nmake -nologo -f "{self._get_configure_dir().joinpath("makefile.vc")}" INSTALLDIR="{self.package_path}" install-binaries install-libraries', cwd=self._get_configure_dir())
        else:
            autotools = Autotools(self)
            autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])  # Need to specify the `DESTDIR` as a Unix path, aware of the subsystem
            autotools.make(target="install-private-headers", args=[f"DESTDIR={unix_path(self, self.package_folder)}"])

            rmdir(self, self.package_path.joinpath("lib", "pkgconfig"))
            rmdir(self, self.package_path.joinpath("share"))
            rmdir(self, self.package_path.joinpath("man"))
            rmdir(self, self.package_path.joinpath("info"))

            package_path = self.package_folder if self.settings.os != "Windows" else unix_path(self, self.package_folder)
            build_folder = self.build_folder if self.settings.os != "Windows" else unix_path(self, self.build_folder)
            tcl_config_sh_path = self.package_path.joinpath("lib", "tclConfig.sh")

            replace_in_file(self, tcl_config_sh_path, package_path, "${TCL_ROOT}", strict=False)
            replace_in_file(self, tcl_config_sh_path, build_folder, "${TCL_BUILD_ROOT}", strict=False)
            replace_in_file(self, tcl_config_sh_path, "//", "${TCL_ROOT}/", strict=False)

            replace_in_file(self, tcl_config_sh_path, "\nTCL_BUILD_", "\n#TCL_BUILD_", strict=False)
            replace_in_file(self, tcl_config_sh_path, "\nTCL_SRC_DIR", "\n#TCL_SRC_DIR", strict=False)

    def package_info(self):
        libs = []
        systemlibs = []
        libdirs = []

        for item in self.package_path.iterdir():
            if item.is_file():
                continue
            newlibs = collect_libs(self, item)
            if newlibs:
                libs.extend(newlibs)
                libdirs.append(str(item))
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

        bin_path = self.package_path.joinpath("bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(str(bin_path))

        version = Version(self.version)
        tcl_library = self.package_path.joinpath("lib", f"{self.name}{version.major}.{version.minor}")
        self.output.info(f"Setting TCL_LIBRARY environment variable to {tcl_library}")
        self.env_info.TCL_LIBRARY = str(tcl_library)
        self.runenv_info.define_path("TCL_LIBRARY", str(tcl_library))
        self.output.info(f"Setting configuration `user.tcl.build:tcl_library` to {tcl_library}")
        self.conf_info.define("user.tcl.build:tcl_library", str(tcl_library))
        self.user_info.tcl_library = str(tcl_library)

        for tcl_lib in self.cpp_info.libs:
            lib_path = self.package_path.joinpath("lib", tcl_lib)
            self.output.info(f"Setting configuration `user.tcl.build:{tcl_lib}` to {lib_path}")
            self.conf_info.define(f"user.tcl.build:{lib_path}", str(lib_path))

        tcl_root = self.package_folder
        self.output.info("Setting TCL_ROOT environment variable to {}".format(tcl_root))
        self.env_info.TCL_ROOT = tcl_root
        self.runenv_info.define_path("TCL_ROOT", tcl_root)

        tclsh = list(self.package_path.joinpath("bin").glob(f"**/tclsh*"))[0]
        self.output.info(f"Setting TCLSH environment variable to {tclsh}")
        self.env_info.TCLSH = str(tclsh)
        self.runenv_info.define_path("TCLSH", str(tclsh))
        self.user_info.tclsh = tclsh
        self.conf_info.define("user.tcl.build:sh", str(tclsh))
        self.user_info.tclsh = tclsh
