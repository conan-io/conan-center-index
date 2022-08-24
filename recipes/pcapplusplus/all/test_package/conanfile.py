from conan import ConanFile, tools
from conans import CMake
import os


class PcapplusplusTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            pcap_file_path = os.path.join(self.source_folder, "1_packet.pcap")
            self.run("{0} {1}".format(bin_path, pcap_file_path), run_environment=True)
