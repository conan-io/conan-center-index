from conans import ConanFile, CMake
from conan.tools.build import cross_building
from conan.tools import files
from io import StringIO
import os


# legacy validation with Conan 1.x
class TestPackageV1Conan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"
    # Needed to make sure libpcap gets compiled
    build_policy = "missing"

    def requirements(self):
        self.requires(self.tested_reference_str)
        if not cross_building(self):
            self.requires("libpcap/1.10.1")

    def configure(self):
        if not cross_building(self):
            self.options["libpcap"].shared = True

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            # Use libpcap DLL as a replacement for npcap DLL
            # It will not provide all the functions
            # but it will cover enough to check that what we compiled is correct
            files.rm(self, "wpcap.dll", "bin")
            files.copy(self, "pcap.dll", src=self.deps_cpp_info['libpcap'].bin_paths[0], dst="bin")
            files.rename(self, os.path.join("bin", "pcap.dll"), os.path.join("bin", "wpcap.dll"))

            bin_path = os.path.join("bin", "test_package")
            output = StringIO()
            self.run(bin_path, run_environment=True, output=output)
            test_output = output.getvalue()
            print(test_output)
            assert "libpcap version 1.10.1" in test_output
