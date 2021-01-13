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
        if tools.cross_building(self.settings):
            return
        img_name = os.path.join(self.source_folder, "testimg.jpg")
        out_img = os.path.join(self.build_folder, "outimg.jpg")
        self.run("%s %s" % (os.path.join("bin", "test_package"), img_name), run_environment=True)
        self.run("%s %s %s" % (os.path.join("bin", "test_transupp"), img_name, out_img), run_environment=True)
