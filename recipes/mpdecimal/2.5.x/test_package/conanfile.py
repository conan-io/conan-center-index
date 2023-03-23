import pathlib
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.build import cross_building


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps"

    def generate(self):
        build_type = self.settings.build_type.value
        tc = CMakeToolchain(self)
        tc.variables["MPDECIMAL_CXX"] = self.options["mpdecimal"].cxx
        tc.variables[f"CMAKE_RUNTIME_OUTPUT_DIRECTORY_{build_type.upper()}"] = "bin"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            self.run("{} 13 100".format(pathlib.Path("bin", "test_package")), run_environment=True)
            if self.options["mpdecimal"].cxx:
                self.run("{} 13 100".format(pathlib.Path("bin", "test_package_cpp")), run_environment=True)
