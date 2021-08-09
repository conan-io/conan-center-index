from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    settings = "os", "compiler", "arch", "build_type"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            arfond = os.path.join(self.source_folder, "example.arfont")
            self.run("{} {}".format(bin_path, arfond), run_environment=True)
