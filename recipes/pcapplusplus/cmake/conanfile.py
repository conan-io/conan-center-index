import os
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.errors import ConanInvalidConfiguration


required_conan_version = ">=1.52.0"

class PcapplusplusConan(ConanFile):
    name = "pcapplusplus"
    package_type = "static-library"
    license = "Unlicense"
    description = "PcapPlusPlus is a multiplatform C++ library for capturing, parsing and crafting of network packets"
    topics = ("pcap", "network", "security", "packet")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/seladb/PcapPlusPlus"
    settings = "os", "arch", "build_type", "compiler"
    options = {
        "immediate_mode": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "immediate_mode": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        if self.settings.os == "Windows":
            self.requires("npcap/1.70")
        else:
            self.requires("libpcap/1.10.1")

    def validate(self):
        if self.settings.os not in ("FreeBSD", "Linux", "Macos", "Windows"):
            raise ConanInvalidConfiguration(f"{self.settings.os} is not supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PCAPPP_BUILD_TESTS"] = False
        tc.variables["PCAPPP_BUILD_EXAMPLES"] = False
        tc.generate()

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"), keep_path=False)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["Pcap++", "Packet++", "Common++"]
        if self.settings.os == "Macos":
            self.cpp_info.frameworks = ["CoreFoundation", "SystemConfiguration"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "iphlpapi"]
        self.cpp_info.set_property("cmake_file_name", "PcapPlusPlus")
        self.cpp_info.set_property("cmake_target_name", "PcapPlusPlus::PcapPlusPlus")
