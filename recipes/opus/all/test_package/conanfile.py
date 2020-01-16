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
        pcm_path = os.path.join(self.source_folder, "test.pcm")
        bin_path = os.path.join("bin", "test_package")
        self.run("%s %s out.pcm" % (bin_path, pcm_path), run_environment=True)
