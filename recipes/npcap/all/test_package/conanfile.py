from conan import ConanFile, conan_version
from conan.tools import files
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
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
            bindir = self.cpp.build.bindir
            # Use libpcap DLL as a replacement for npcap DLL
            # It will not provide all the functions
            # but it will cover enough to check that what we compiled is correct
            files.rm(self, "wpcap.dll", bindir)
            libpcap_bin_path = self.deps_cpp_info["libpcap"].bin_paths[0] if conan_version < "2" else self.dependencies["libpcap"].cpp_info.bindirs[0]
            files.copy(self, "pcap.dll", src=libpcap_bin_path, dst=os.path.join(str(self.build_path), bindir))
            files.rename(self, os.path.join(bindir, "pcap.dll"), os.path.join(bindir, "wpcap.dll"))

            self.run(os.path.join(bindir, "test_package"), env="conanrun")
