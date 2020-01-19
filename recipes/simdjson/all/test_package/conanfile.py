from conans import ConanFile, CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        img_name = os.path.join(self.source_folder, "testimg.jpg")
        bin_path = os.path.join("bin", "test_package")
        self.run('%s %s' % (bin_path, img_name), run_environment=True)
