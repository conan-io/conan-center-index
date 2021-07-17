from conans import ConanFile, CMake
import os


class PcapplusplusTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def configure(self):
        pass
        # del self.settings.compiler.libcxx

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        bin_path = os.path.join("bin", "test_package")
        pcap_file_path = os.path.join(self.source_folder, "1_packet.pcap")
        self.run("{0} {1}".format(bin_path, pcap_file_path), run_environment=True)
