import os
import pathlib
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.build import can_run


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):

        tc = CMakeToolchain(self)
        tc.variables["MPDECIMAL_CXX"] = self.dependencies["mpdecimal"].options.cxx
        if self.settings.os != "Windows":
            build_type = self.settings.build_type.value
            tc.variables[f"CMAKE_RUNTIME_OUTPUT_DIRECTORY_{build_type.upper()}"] = "bin"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            if self.settings.os != "Windows":
                bin_path = pathlib.Path(self.cpp.build.bindirs[0], "bin", "test_package")
            else:
                bin_path = pathlib.Path(self.cpp.build.bindirs[0], "test_package")
            self.run(f"{bin_path} 13 100", env="conanrun")
            if os.path.exists(pathlib.Path(self.cpp.build.bindirs[0], "test_package_cpp")):
                if self.settings.os != "Windows":
                    bin_path = pathlib.Path(self.cpp.build.bindirs[0], "bin", "test_package")
                else:
                    bin_path = pathlib.Path(self.cpp.build.bindirs[0], "test_package")
                self.run(f"{bin_path} 13 100", env="conanrun")
