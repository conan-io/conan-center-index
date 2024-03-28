from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
from conan.tools.env import Environment
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        env = Environment()
        # Trigger printing of runtime version info on startup
        env.define("KMP_VERSION", "TRUE")
        env.vars(self, scope="run").save_script("conan_openmp_version")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            for executable in ["test_package_cxx", "test_package_c"]:
                bin_path = os.path.join(self.cpp.build.bindir, executable)
                self.run(bin_path, env="conanrun")
