from conan import ConanFile
from conan.tools.cmake import cmake_layout, CMake


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain"
    
    def layout(self):
        cmake_layout(self)
    
    def requirements(self):
        self.requires(self.tested_reference_str)
    
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
    
    def test(self):
        self.run(f"{self.cpp.build.bindir}/test_akasha", env="conanrun")
