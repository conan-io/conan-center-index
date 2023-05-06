import os

from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import (
    apply_conandata_patches,
    chdir,
    copy,
    export_conandata_patches,
    get,
    replace_in_file,
    rmdir,
)
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import NMakeDeps, NMakeToolchain, is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.55.0"


class TkConan(ConanFile):
    name = "tk"
    description = "Tk is a graphical user interface toolkit that takes developing desktop applications to a higher level than conventional approaches."
    topics = ("conan", "tk", "gui", "tcl", "scripting", "programming")
    homepage = "https://tcl.tk"
    license = "TCL"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def requirements(self):
        self.requires(
            f"tcl/{self.version}", transitive_headers=True, transitive_libs=True
        )
        if self.settings.os == "Linux":
            self.requires("fontconfig/2.13.93")
            self.requires("xorg/system")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if not is_msvc(self):
            if (
                self._settings_build.os == "Windows"
                and not self.conf.get("tools.microsoft.bash:path")
                and not self.conf.get("tools.microsoft.bash:subsystem")
            ):
                self.build_requires("msys2/cci.latest")

    def validate(self):
        if self.dependencies["tcl"].options.shared != self.options.shared:
            raise ConanInvalidConfiguration(
                "The shared option of tcl and tk must have the same value"
            )

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(
            self,
            **self.conan_data["sources"][self.version],
            strip_root=True,
            destination=self.source_folder,
        )

    def generate(self):
        buildenv = VirtualBuildEnv(self)
        buildenv.generate()

        if is_msvc(self):
            # https://core.tcl.tk/tips/doc/trunk/tip/477.md
            opts = []
            if not self.options.shared:
                opts.append("static")
            if self.settings.build_type == "Debug":
                opts.append("symbols")
            if "MD" in str(self.settings.compiler.runtime):
                opts.append("msvcrt")
            else:
                opts.append("nomsvcrt")
            if "d" not in str(self.settings.compiler.runtime):
                opts.append("unchecked")
            # https://core.tcl.tk/tk/tktview?name=3d34589aa0
            # https://wiki.tcl-lang.org/page/Building+with+Visual+Studio+2017
            tcl_lib_path = os.path.join(self.dependencies["tcl"].package_folder, "lib")
            tclimplib, tclstublib = None, None
            for lib in os.listdir(tcl_lib_path):
                if not lib.endswith(".lib"):
                    continue
                if lib.startswith("tcl{}".format("".join(self.version.split(".")[:2]))):
                    tclimplib = os.path.join(tcl_lib_path, lib)
                elif lib.startswith(
                    "tclstub{}".format("".join(self.version.split(".")[:2]))
                ):
                    tclstublib = os.path.join(tcl_lib_path, lib)

            if tclimplib is None or tclstublib is None:
                raise ConanException("tcl dependency misses tcl and/or tclstub library")

            tc = NMakeToolchain(self)
            tc.extra_defines.append(f"INSTALLDIR={self.package_folder}")
            tc.extra_defines.append(f"OPTS={','.join(opts)}")
            tc.extra_defines.append(f"TCLDIR={self.dependencies['tcl'].package_folder}")
            tc.extra_defines.append(
                f"TCL_LIBRARY={self.dependencies['tcl'].runenv_info.vars.get('TCL_LIBRARY')}"
            )
            tc.extra_defines.append(f"TCLIMPLIB={tclimplib}")
            tc.extra_defines.append(f"TCLSTUBLIB={tclstublib}")
            tc.generate()

            deps = NMakeDeps(self)
            deps.generate()
        else:
            # Inject runenv variables into buildenv
            # This is required because tcl needs to be available when configure tries to
            # run a test executable
            if not cross_building(self):
                runenv = VirtualRunEnv(self)
                runenv.generate(scope="build")

            yes_no = lambda v: "yes" if v else "no"
            tc = AutotoolsToolchain(self)
            tc.configure_args.append("--enable-threads")
            tc.configure_args.append(
                f"--enable-symbols={yes_no(self.settings.build_type == 'Debug')}"
            )
            tc.configure_args.append(
                f"--enable-64bit={yes_no(self.settings.arch == 'x86_64')}"
            )
            tc.configure_args.append(f"--enable-aqua={yes_no(is_apple_os(self))}")
            tc.configure_args.append(
                f"--with-tcl={os.path.join(self.dependencies['tcl'].package_folder, 'lib')}"
            )
            tc.configure_args.append(f"--with-x={yes_no(self.settings.os == 'Linux')}")
            tc.make_args.append(
                f"TCL_GENERIC_DIR={os.path.join(self.dependencies['tcl'].package_folder, 'include')}"
            )
            if self.settings.os == "Windows":
                tc.extra_defines.extend(
                    [
                        "UNICODE",
                        "_UNICODE",
                        "_ATL_XP_TARGETING",
                    ]
                )
            tc.generate()

            deps = AutotoolsDeps(self)
            deps.generate()

    def _get_default_build_system(self):
        if is_apple_os(self):
            return "macosx"
        elif self.settings.os in ("Linux", "FreeBSD"):
            return "unix"
        elif self.settings.os == "Windows":
            return "win"
        else:
            raise ValueError("tk recipe does not recognize os")

    def _get_configure_folder(self, build_system=None):
        if build_system is None:
            build_system = self._get_default_build_system()
        if build_system not in ["win", "unix", "macosx"]:
            raise ConanException(f"Invalid build system: {build_system}")
        return os.path.join(self.source_folder, build_system)

    def _build_nmake(self, target="release"):
        self.run(f"nmake -nologo -f win/makefile.vc {target}")

    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            self._build_nmake()
        else:
            autotools = Autotools(self)
            autotools.configure(build_script_folder=self._get_configure_folder())
            autotools.make()

    def package(self):
        copy(self, pattern="license.terms", src=self.source_folder, dst="licenses")
        if is_msvc(self):
            self._build_nmake("install")
        else:
            with chdir(self, self.build_folder):
                autotools = Autotools(self)
                autotools.install()
                # DESTDIR is only default initialized for target="install"
                autotools.make(
                    target="install-private-headers",
                    args=[f"DESTDIR={self.package_folder}"],
                )
                rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "man"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        tkConfigShPath = os.path.join(self.package_folder, "lib", "tkConfig.sh")
        if os.path.exists(tkConfigShPath):
            # This can only be modified after build since the value being replaced is a result
            # of variable substitution in tkConfig.sh.in
            replace_in_file(self, tkConfigShPath, "//", "${TK_ROOT}/")

    def package_info(self):
        tk_version = Version(self.version)
        lib_infix = f"{tk_version.major}.{tk_version.minor}"
        if is_msvc(self):
            tk_suffix = "t{}{}{}".format(
                "" if self.options.shared else "s",
                "g" if self.settings.build_type == "Debug" else "",
                "x" if "MD" in str(self.settings.compiler.runtime) and not self.options.shared else "",
            )
        else:
            tk_suffix = ""
        self.cpp_info.libs = [f"tk{lib_infix}{tk_suffix}", f"tkstub{lib_infix}"]
        if self.settings.os == "Macos":
            self.cpp_info.frameworks = ["CoreFoundation", "Cocoa", "Carbon", "IOKit"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = [
                "netapi32",
                "kernel32",
                "user32",
                "advapi32",
                "userenv",
                "ws2_32",
                "gdi32",
                "comdlg32",
                "imm32",
                "comctl32",
                "shell32",
                "uuid",
                "ole32",
                "oleaut32",
            ]

        tk_library = os.path.join(
            self.package_folder,
            "lib",
            f"{self.name}{tk_version.major}.{tk_version.minor}",
        ).replace("\\", "/")
        self.output.info(f"Setting TK_LIBRARY environment variable: {tk_library}")
        self.env_info.TK_LIBRARY = tk_library
        self.runenv_info.define("TK_LIBRARY", tk_library)

        tk_root = self.package_folder.replace("\\", "/")
        self.output.info(f"Setting TK_ROOT environment variable: {tk_root}")
        self.env_info.TK_ROOT = tk_root
        self.runenv_info.define("TK_ROOT", tk_root)
