from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
from conan.tools.env import Environment
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "PkgConfigDeps", "VirtualBuildEnv", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.2.0")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        env = Environment()
        # Trigger printing of runtime version info on startup.
        # Should state "LLVM OMP" as the runtime library ID if everything is configured correctly.
        env.define("KMP_VERSION", "TRUE")
        # Display general OpenMP parameters in a standardized format.
        # https://www.openmp.org/spec-html/5.0/openmpse60.html
        env.define("OMP_DISPLAY_ENV", "TRUE")
        env.vars(self, scope="run").save_script("conan_openmp_version")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            for executable in ["test_package_cxx", "test_package_c", "test_package_pkgconfig"]:
                bin_path = os.path.join(self.cpp.build.bindir, executable)
                self.run(bin_path, env="conanrun")
