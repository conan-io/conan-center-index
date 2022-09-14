from pathlib import Path

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.apple import is_apple_os
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import collect_libs, copy, get, replace_in_file, rmdir, load
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, msvc_runtime_flag, unix_path, VCVars
from conan.tools.scm import Version

required_conan_version = ">=1.51.3"


class TkConan(ConanFile):
    name = "tk"
    description = "Tk is a graphical user interface toolkit that takes developing desktop applications to a higher level than conventional approaches."
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
        self.options["tcl"].shared = self.options.shared

    def layout(self):
        basic_layout(self, src_folder="tk")

    def requirements(self):
        self.requires("tcl/{}".format(self.version))
        if self.settings.os == "Linux":
            self.requires("fontconfig/2.13.93")
            self.requires("xorg/system")

    def validate(self):
        if is_msvc(self) and self.options.shared != ("MD" in msvc_runtime_flag(self)):
            raise ConanInvalidConfiguration(f"compiler.runtime = {self.settings.get_safe('compiler.runtime')} while tcl:shared = {self.options.shared}")
        if self.options["tcl"].shared != self.options.shared:
            raise ConanInvalidConfiguration("The shared option of tcl and tk must have the same value")

    def build_requirements(self):
        if self.win_bash and not self.conf.get("tools.microsoft.bash:path", default=False, check_type=bool):
            self.tool_requires("msys2/cci.latest")
        if not is_msvc(self):
            self.tool_requires("automake/1.16.5")
        self.tool_requires("tcl/{}".format(self.version))

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
            tcl_root = Path(self.deps_cpp_info["tcl"].rootpath)

            tc.make_args.extend([
                f"TCL_GENERIC_DIR={unix_path(self, str(tcl_root.joinpath('include')))}",
            ])

            # The default Autotools configuration flags are not used by Tcl
            tc.configure_args = tc._default_configure_install_flags() + [
                "--datadir=${prefix}/res",
                "--enable-threads",
                f"--enable-shared={yes_no(self.options.shared)}",
                f"--enable-symbols={yes_no(self.settings.build_type == 'Debug')}",
                f"--enable-64bit={yes_no(self.settings.arch == 'x86_64')}",
                f"--with-x={yes_no(self.settings.os == 'Linux')}",
                f"--with-tcl={unix_path(self, str(tcl_root.joinpath('lib')))}",
                f"--enable-aqua={yes_no(is_apple_os(self))}",
            ]

            if self.settings.os == "Windows":
                tc.extra_defines.extend([
                    "UNICODE",
                    "_UNICODE",
                    "_ATL_XP_TARGETING",
                ])

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
        for build_system in ("unix", "win", ):
            config_dir = self._get_configure_dir(build_system)

            if build_system != "win":
                # When disabling 64-bit support (in 32-bit), this test must be 0 in order to use "long long" for 64-bit ints
                # (${tcl_type_64bit} can be either "__int64" or "long long")
                replace_in_file(self, config_dir.joinpath("configure"), "(sizeof(${tcl_type_64bit})==sizeof(long))", "(sizeof(${tcl_type_64bit})!=sizeof(long))")

            makefile_in = config_dir.joinpath("Makefile.in")
            # Avoid clearing CFLAGS and LDFLAGS in the makefile
            # tools.replace_in_file(makefile_in, "\nCFLAGS{}".format(" " if (build_system == "win" and name == "tcl") else "\t"), "\n#CFLAGS\t")
            replace_in_file(self, makefile_in, "\nLDFLAGS\t", "\n#LDFLAGS\t")
            replace_in_file(self, makefile_in, "${CFLAGS}", "${CFLAGS} ${CPPFLAGS}")

        rules_ext_vc = self.source_path.joinpath("win", "rules-ext.vc")
        replace_in_file(self, rules_ext_vc, "\n_RULESDIR = ", "\n_RULESDIR = .\n#_RULESDIR = ")
        rules_vc = self.source_path.joinpath("win", "rules.vc")
        replace_in_file(self, rules_vc, r"$(_TCLDIR)\generic", r"$(_TCLDIR)\include")
        replace_in_file(self, rules_vc, "\nTCLSTUBLIB", "\n#TCLSTUBLIB")
        replace_in_file(self, rules_vc, "\nTCLIMPLIB", "\n#TCLIMPLIB")

        win_makefile_in = self._get_configure_dir("win").joinpath("Makefile.in")
        replace_in_file(self, win_makefile_in, "\nTCL_GENERIC_DIR", "\n#TCL_GENERIC_DIR")

        win_rules_vc = self.source_path.joinpath("win", "rules.vc")
        replace_in_file(self, win_rules_vc, "\ncwarn = $(cwarn) -WX", "\n# cwarn = $(cwarn) -WX")

        # disable whole program optimization to be portable across different MSVC versions.
        # See conan-io/conan-center-index#4811 conan-io/conan-center-index#4094
        replace_in_file(self, win_rules_vc, "OPTIMIZATIONS  = $(OPTIMIZATIONS) -GL", "# OPTIMIZATIONS  = $(OPTIMIZATIONS) -GL")

    @property
    def _nmake(self):
        # https://core.tcl.tk/tk/tktview?name=3d34589aa0
        # https://wiki.tcl-lang.org/page/Building+with+Visual+Studio+2017
        tclimplib = self.conf.get("user.tcl.build:tcl")
        tclstublib = self.conf.get("user.tcl.build:tclstub")
        tcldir = self.deps_cpp_info["tcl"].rootpath
        return f'nmake -nologo -f "{self._get_configure_dir().joinpath("makefile.vc")}" INSTALLDIR="{self.package_path}" TCLDIR="{tcldir}" TCLIMPLIB={tclimplib} TCLSTUBLIB={tclstublib}'

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

            self.run(f"{self._nmake} OPTS={opts_arg} {str(self.settings.build_type).lower()}", cwd=self._get_configure_dir())
        else:
            autotools = Autotools(self)
            try:
                autotools.configure(build_script_folder=self._get_configure_dir())
            except ConanException as e:
                autotools_config_log = self.build_path.joinpath("config.log")
                if autotools_config_log.exists():
                    self.output.info(load(self, autotools_config_log))
                raise ConanException(e)
            autotools.make()

    def package(self):
        copy(self, "license.terms", src=self.source_folder, dst=self.package_path.joinpath("licenses"))

        if is_msvc(self):
            self.run(f"{self._nmake} install-binaries install-libraries", cwd=self._get_configure_dir())
        else:
            autotools = Autotools(self)
            autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])  # Need to specify the `DESTDIR` as a Unix path, aware of the subsystem
            autotools.make(target="install-private-headers", args=[f"DESTDIR={unix_path(self, self.package_folder)}"])

            rmdir(self, self.package_path.joinpath("lib", "pkgconfig"))
            rmdir(self, self.package_path.joinpath("share"))
            rmdir(self, self.package_path.joinpath("info"))

            package_path = self.package_folder if self.settings.os != "Windows" else unix_path(self, self.package_folder)
            tcl_config_sh_path = self.package_path.joinpath("lib", "tkConfig.sh")

            replace_in_file(self, tcl_config_sh_path, package_path, "${TK_ROOT}", strict=False)
            replace_in_file(self, tcl_config_sh_path, "//", "${TK_ROOT}/", strict=False)

            replace_in_file(self, tcl_config_sh_path, "\nTK_BUILD_", "\n#TK_BUILD_", strict=False)
            replace_in_file(self, tcl_config_sh_path, "\nTK_SRC_DIR", "\n#TK_SRC_DIR", strict=False)

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
            systemlibs.extend(["netapi32", "kernel32", "user32", "advapi32", "userenv", "ws2_32", "gdi32", "comdlg32",
                               "imm32", "comctl32", "shell32", "uuid", "ole32", "oleaut32"])
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks = ["CoreFoundation", "Cocoa", "Carbon", "IOKit"]

        self.cpp_info.libdirs = libdirs
        self.cpp_info.libs = libs
        self.cpp_info.system_libs = systemlibs

        bin_path = self.package_path.joinpath("bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(str(bin_path))

        version = Version(self.version)
        tk_library = self.package_path.joinpath("lib", f"{self.name}{version.major}.{version.minor}")
        self.output.info(f"Setting TK_LIBRARY environment variable to {tk_library}")
        self.env_info.TK_LIBRARY = str(tk_library)
        self.runenv_info.define_path("TK_LIBRARY", str(tk_library))
        self.conf_info.define("user.tk.build:library", str(tk_library))
        self.user_info.tk_library = str(tk_library)

        tk_root = self.package_folder
        self.output.info("Setting TK_ROOT environment variable to {}".format(tk_root))
        self.env_info.TK_ROOT = tk_root
        self.runenv_info.define_path("TK_ROOT", tk_root)
