from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
import os

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    generators = "CMakeDeps", "CMakeToolchain"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires("qt/[>=6.0.0]")
        self.requires("runtimeqml/latest")

    def configure(self):
        self.options["qt"].shared = True
        self.options["qt"].qtdeclarative = True
        self.options["qt"].qtshadertools = True
        self.options["qt"].with_libjpeg = "libjpeg-turbo"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
    
    def test(self):
        # if self.settings.os == "Windows":
        #     self.run(os.path.join(self.build_folder, "bin/RuntimeQmlTest.exe"))
        # else:
        #     self.run(os.path.join(self.build_folder, "build/bin/RuntimeQmlTest"))
        bin_path = os.path.join("bin", "RuntimeQmlTest")
        self.run(bin_path, run_environment=True)