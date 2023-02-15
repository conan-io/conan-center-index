from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import get, copy, rmdir, export_conandata_patches, apply_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path, check_min_vs
import os

required_conan_version = ">=1.53.0"


class ImakeConan(ConanFile):
    name = "imake"
    description = "Obsolete C preprocessor interface to the make utility"
    topics = ("xmkmf", "preprocessor", "build", "system")
    license = "MIT"
    homepage = "https://gitlab.freedesktop.org/xorg/util/imake"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "ccmakedep": [True, False],
        "cleanlinks": [True, False],
        "makeg": [True, False],
        "mergelib": [True, False],
        "mkdirhier": [True, False],
        "mkhtmlindex": [True, False],
        "revpath": [True, False],
        "xmkmf": [True, False],
    }
    default_options = {
        "ccmakedep": True,
        "cleanlinks": True,
        "makeg": True,
        "mergelib": True,
        "mkdirhier": True,
        "mkhtmlindex": True,
        "revpath": True,
        "xmkmf": True,
    }

    def layout(self):
        basic_layout(self, src_folder="src")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def requirements(self):
        self.requires("xorg-proto/2021.4")

    def build_requirements(self):
        self.tool_requires("automake/1.16.5")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/1.9.3")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def export_sources(self):
        export_conandata_patches(self)

    def generate(self):
        venv = VirtualBuildEnv(self)
        venv.generate()

        tc = AutotoolsToolchain(self)

        if self.settings.os == "Windows":
            tc.extra_defines.append("WIN32")
        if is_msvc(self):
            tc.extra_defines.extend([
                "_CRT_SECURE_NO_WARNINGS",
                "CROSSCOMPILE_CPP",
            ])
            if check_min_vs(self, "180", raise_invalid=False):
                tc.extra_cflags.append("-FS")
                tc.extra_cxxflags.append("-FS")

        yes_no = lambda v: "yes" if v else "no"
        conf_args = [
            "--enable-ccmakedep={}".format(yes_no(self.options.ccmakedep)),
            "--enable-cleanlinks={}".format(yes_no(self.options.cleanlinks)),
            "--enable-makeg={}".format(yes_no(self.options.makeg)),
            "--enable-mergelib={}".format(yes_no(self.options.mergelib)),
            "--enable-mkdirhier={}".format(yes_no(self.options.mkdirhier)),
            "--enable-mkhtmlindex={}".format(yes_no(self.options.mkhtmlindex)),
            "--enable-revpath={}".format(yes_no(self.options.revpath)),
            "--enable-xmkmf={}".format(yes_no(self.options.xmkmf)),
        ]
        if "CPP" in os.environ:
            conf_args.extend([
                "--with-script-preproc-cmd={}".format(os.environ["CPP"]),
            ])

        env = tc.environment()
        if is_msvc(self):
            compile_wrapper = f"{unix_path(self, self.conf.get('user.automake:compile-wrapper'))} cl -nologo"
            env.define("CC", compile_wrapper)
            env.define("CXX", compile_wrapper)
            env.define("CPP", compile_wrapper)
        tc.generate(env)

        pkgconf = PkgConfigDeps(self)
        pkgconf.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.configure()
        autotools.make(args=["V=1"])

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
