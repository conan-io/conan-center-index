from conans import ConanFile, CMake
import os


class DefaultNameConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        bin_path = os.path.join("bin", "test_package")
        imgfile = os.path.join(self.source_folder, "comp_short_decode_piz.exr")
        self.run("{} {}".format(bin_path, imgfile), run_environment=True)
