from conans import ConanFile, CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def requirements(self):
        self.requires("glfw/3.3.4")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        bin_path = os.path.join("bin", "test_package")
        img_path = os.path.join(self.source_folder, "img_test.png")
        self.run("%s %s" % (bin_path, img_path), run_environment=True)
