from conan import ConanFile
from conan.tools.build import can_run
from conans import CMake, tools
import os
import shutil


class PcapplusplusTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    # Needed to make sure libpcap gets compiled
    build_policy = "missing"

    def requirements(self):
        self.requires(self.tested_reference_str)
        if can_run(self):
            self.requires("libpcap/1.10.1")

    def configure(self):
        if can_run(self):
            self.options["libpcap"].shared = True

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            # Use libpcap DLL as a replacement for npcap DLL
            # It will not provide all the functions
            # but it will cover enough to check that what we compiled is correct
            shutil.copy(
                os.path.join(self.deps_cpp_info['libpcap'].bin_paths[0], "pcap.dll"),
                os.path.join("bin", "wpcap.dll")
            )
            bin_path = os.path.join("bin", "test_package")
            pcap_file_path = os.path.join(self.source_folder, "1_packet.pcap")
            self.run(f"{bin_path} {pcap_file_path}", run_environment=True)
