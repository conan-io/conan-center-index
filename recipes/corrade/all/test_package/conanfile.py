from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        if self.settings.compiler == "Visual Studio":
            cmake.definitions["CORRADE_MSVC2015_COMPATIBILITY"] = "ON" if self.settings.compiler.version == "14" else "OFF"
            cmake.definitions["CORRADE_MSVC2017_COMPATIBILITY"] = "ON" if self.settings.compiler.version == "15" else "OFF"
            cmake.definitions["CORRADE_MSVC2019_COMPATIBILITY"] = "ON" if self.settings.compiler.version == "16" else "OFF"
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
