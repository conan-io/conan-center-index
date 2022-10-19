from conan import ConanFile
from conan.tools.cmake import CMake
import os

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    generators = "CMakeDeps", "CMakeToolchain"

    def configure(self):
        qt = self.dependencies["qt"]
        qt.options.qtdeclarative = True

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
    
    def test(self):
        bin_path = os.path.join("bin", "RuntimeQmlTest")
        self.run(bin_path, run_environment=True)
