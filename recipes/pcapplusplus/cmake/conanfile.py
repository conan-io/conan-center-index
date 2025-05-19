import os
from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import copy, get, rmdir, replace_in_file
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration


required_conan_version = ">=2"


class PcapplusplusConan(ConanFile):
    name = "pcapplusplus"
    license = "Unlicense"
    description = "PcapPlusPlus is a multiplatform C++ library for capturing, parsing and crafting of network packets"
    topics = ("pcap", "network", "security", "packet")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/seladb/PcapPlusPlus"
    settings = "os", "arch", "build_type", "compiler"
    package_type = "library"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "immediate_mode": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
        "immediate_mode": False,
    }

    implements = ["auto_shared_fpic"]

    def requirements(self):
        if self.settings.os == "Windows":
            self.requires("npcap/1.70")
        else:
            self.requires("libpcap/1.10.1")

    def validate(self):
        if Version(self.version) <= "25.05" and self.options.shared and self.settings.os == "Windows":
            # https://github.com/seladb/PcapPlusPlus/issues/1396
            raise ConanInvalidConfiguration(f"{self.ref} does not support Windows shared builds for now")
        check_min_cppstd(self, 11)
        if self.settings.os not in ("FreeBSD", "Linux", "Macos", "Windows"):
            raise ConanInvalidConfiguration(f"{self.settings.os} is not supported")

    def validate_build(self):
        compiler_version = Version(self.settings.compiler.version)
        if self.settings.compiler == "gcc" and compiler_version < "5.1":
            raise ConanInvalidConfiguration("PcapPlusPlus requires GCC >= 5.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        self._patch_sources()

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["PCAPPP_BUILD_TESTS"] = False
        tc.cache_variables["PCAPPP_BUILD_EXAMPLES"] = False
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.generate()

    def layout(self):
        cmake_layout(self, src_folder="src")

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "set(CMAKE_CXX_STANDARD 11)",
                        "")
        if Version(self.version) >= "24.09":
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            "set(CMAKE_POSITION_INDEPENDENT_CODE ON)",
                            "")

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
        self.cpp_info.set_property("cmake_file_name", "PcapPlusPlus")
        self.cpp_info.set_property("cmake_target_name", "PcapPlusPlus::PcapPlusPlus")

        self.cpp_info.components["common"].libs = ["Common++"]
        if self.settings.os == "Windows":
            self.cpp_info.components["common"].system_libs = ["ws2_32", "iphlpapi"]

        self.cpp_info.components["packet"].libs = ["Packet++"]
        self.cpp_info.components["packet"].requires = ["common"]

        self.cpp_info.components["pcap"].libs = ["Pcap++"]
        self.cpp_info.components["pcap"].requires = ["common", "packet"]
        if self.settings.os == "Windows":
            self.cpp_info.components["pcap"].requires.append("npcap::npcap")
            self.cpp_info.components["pcap"].system_libs = ["ws2_32", "iphlpapi"]
            self.cpp_info.components["pcap"].defines = ["WPCAP", "HAVE_REMOTE"]
        else:
            self.cpp_info.components["pcap"].requires.append("libpcap::libpcap")

        if self.settings.os == "Macos":
            self.cpp_info.components["pcap"].frameworks = ["CoreFoundation", "SystemConfiguration"]
        elif self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["pcap"].system_libs = ["pthread"]
