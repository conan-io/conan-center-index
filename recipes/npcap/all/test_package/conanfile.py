from conan import ConanFile
from conan.tools import files
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
from io import StringIO
import os


# It will become the standard on Conan 2.x
class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)
        if can_run(self):
            self.requires("libpcap/1.10.1")

    def configure(self):
        if can_run(self):
            self.options["libpcap"].shared = True

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bindir = self.cpp.build.bindirs[0]
            # Use libpcap DLL as a replacement for npcap DLL
            # It will not provide all the functions
            # but it will cover enough to check that what we compiled is correct
            files.rm(self, "wpcap.dll", bindir)
            files.copy(self, "pcap.dll", src=self.deps_cpp_info['libpcap'].bin_paths[0], dst=bindir)
            files.rename(self, os.path.join(bindir, "pcap.dll"), os.path.join(bindir, "wpcap.dll"))

            bin_path = os.path.join(bindir, "test_package")
            output = StringIO()
            self.run(bin_path, env="conanrun", output=output)
            test_output = output.getvalue()
            print(test_output)
            assert "libpcap version 1.10.1" in test_output
