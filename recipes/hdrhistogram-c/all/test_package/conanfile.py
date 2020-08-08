from conans import ConanFile, CMake, tools
import os


class HDRHistogramCTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "hdr_decoder_c")
            self.run(bin_path, run_environment=True)

            bin_path = os.path.join("bin", "hdr_decoder_cxx")
            self.run(bin_path, run_environment=True)
