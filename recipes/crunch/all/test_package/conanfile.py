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
            img_path = os.path.join(self.source_folder, "test.png")
            self.run("crunch -file {}".format(img_path), run_environment=True)

            bin_path = os.path.join("bin", "test_package")
            self.run("{}".format(bin_path), run_environment=True)
