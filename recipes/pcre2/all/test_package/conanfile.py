from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            arguments = "%sw+ Bincrafters" % ("\\" if self.settings.os == "Windows" else "\\\\")
            self.run("%s %s" % (bin_path, arguments), run_environment=True)
