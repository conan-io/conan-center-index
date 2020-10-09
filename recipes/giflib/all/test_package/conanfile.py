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
        img_name = os.path.join(self.source_folder, "testimg.gif")
        bin_path = os.path.join("bin", "test_package")
        command = "%s %s" % (bin_path, img_name)
        self.run(command, run_environment=True)
