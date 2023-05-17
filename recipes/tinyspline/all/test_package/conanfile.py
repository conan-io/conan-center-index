from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["TINYSPLINE_CXX"] = self.dependencies["tinyspline"].options.cxx
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_c_path = os.path.join(self.cpp.build.bindirs[0], "test_package_c")
            self.run(bin_c_path, run_environment=True)

            # TODO: rely on self.dependencies["tinyspline"].options.cxx in CONAN_V2 mode
            # see https://github.com/conan-io/conan/issues/11940#issuecomment-1223940786
            bin_cpp_path = os.path.join(self.cpp.build.bindirs[0], "test_package_cpp")
            if os.path.exists(bin_cpp_path):
                self.run(bin_cpp_path, run_environment=True)
