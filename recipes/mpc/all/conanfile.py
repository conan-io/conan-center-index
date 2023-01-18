from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import chdir, copy, get, rmdir, rm, apply_conandata_patches
from conan.tools.layout import basic_layout
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.microsoft import is_msvc, unix_path
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.56.0"

class MpcConan(ConanFile):
    name = "mpc"
    package_type = "library"
    description = "GNU MPC is a C library for the arithmetic of complex numbers with arbitrarily high precision " \
                  "and correct rounding of the result"
    topics = ("conan", "mpc", "multiprecision", "math", "mathematics")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.multiprecision.org/mpc/home.html"
    license = "LGPL-3.0-or-later"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = "patches/**"

    def config_options(self):
        if self.settings.os == 'Windows':
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def requirements(self):
        self.requires("gmp/6.2.1", transitive_headers=True)
        self.requires("mpfr/4.1.0", transitive_headers=True)

    def validate(self):
        # FIXME: add msvc support, upstream has a makefile.vc
        if self.info.settings.compiler == "msvc":
            raise ConanInvalidConfiguration("mpc can be built with msvc, but it's not supported yet in this recipe.")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            self.tool_requires("automake/1.16.5") # Neededfor lib-wrapper
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        tc.configure_args.append(f'--with-gmp={unix_path(self, self.dependencies["gmp"].package_folder)}')
        tc.configure_args.append(f'--with-mpfr={unix_path(self, self.dependencies["mpfr"].package_folder)}')
        if self.options.shared:
            tc.configure_args.extend(["--disable-static", "--enable-shared"])
        else:
            tc.configure_args.extend(["--disable-shared", "--enable-static"])

        env = tc.environment() # Environment must be captured *after* setting extra_cflags, etc. to pick up changes
        if is_msvc(self):
            ar_wrapper = unix_path(self, self.conf.get("user.automake:lib-wrapper"))
            env.define("CC", "cl -nologo")
            env.define("CXX", "cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f'{ar_wrapper} "lib -nologo"')
        tc.generate(env) # Create conanbuild.conf

        tc = AutotoolsDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        with chdir(self, self.source_folder):
            if not os.path.exists("configure"):
                command = "autoreconf -i"
                self.run(command)
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING.LESSER", self.source_folder, os.path.join(self.package_folder, "licenses"), keep_path=False)
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"), recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "MPC")
        self.cpp_info.set_property("cmake_module_file_name", "mpc")
        self.cpp_info.set_property("cmake_target_name", "MPC::MPC")
        self.cpp_info.libs = ["mpc"]
