from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.layout import basic_layout
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.apple import fix_apple_shared_install_name
from conan.errors import ConanInvalidConfiguration
import os


required_conan_version = ">=1.54.0"

class MpcConan(ConanFile):
    name = "mpc"
    description = "GNU MPC is a C library for the arithmetic of complex numbers with arbitrarily high precision " \
                  "and correct rounding of the result"
    license = "LGPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.multiprecision.org/"
    topics = ("multiprecision", "math", "mathematics")
    settings = "os", "arch", "compiler", "build_type"
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
        if self.settings.os == 'Windows':
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("gmp/6.3.0", transitive_headers=True)
        self.requires("mpfr/4.2.0", transitive_headers=True)

    def validate(self):
        # FIXME: add msvc support, upstream has a makefile.vc
        if is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.ref} can be built with msvc, but it's not supported yet in this recipe.")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        tc.configure_args.append(f'--with-gmp={unix_path(self, self.dependencies["gmp"].package_folder)}')
        tc.configure_args.append(f'--with-mpfr={unix_path(self, self.dependencies["mpfr"].package_folder)}')
        tc.generate()

        tc = AutotoolsDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        if not os.path.exists(os.path.join(self.source_folder, "configure")):
            autotools.autoreconf(["-i"])
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING.LESSER", self.source_folder, os.path.join(self.package_folder, "licenses"), keep_path=False)
        autotools = Autotools(self)
        autotools.install()
        fix_apple_shared_install_name(self)
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"), recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["mpc"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
