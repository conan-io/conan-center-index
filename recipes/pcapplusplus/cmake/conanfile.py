import os
from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import copy, get, rmdir, replace_in_file
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration


required_conan_version = ">=1.52.0"


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

    @property
    def _min_cppstd(self):
        return 11

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        if self.settings.os == "Windows":
            self.requires("npcap/1.70")
        else:
            self.requires("libpcap/1.10.1")
    
    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def validate(self):
        if Version(self.version) <= "24.09" and self.options.shared and self.settings.os == "Windows":
            # https://github.com/seladb/PcapPlusPlus/issues/1396
            raise ConanInvalidConfiguration(f"{self.ref} does not support Windows shared builds for now")
        if self.settings.compiler.cppstd:
            # popen()/pclose() usage
            check_min_cppstd(self, self._min_cppstd)
        if self.settings.os not in ("FreeBSD", "Linux", "Macos", "Windows"):
            raise ConanInvalidConfiguration(f"{self.settings.os} is not supported")

    def validate_build(self):
        compiler_version = Version(self.settings.compiler.version)
        if self.settings.compiler == "gcc" and compiler_version < "5.1":
            raise ConanInvalidConfiguration("PcapPlusPlus requires GCC >= 5.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PCAPPP_BUILD_TESTS"] = False
        tc.variables["PCAPPP_BUILD_EXAMPLES"] = False
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        if not self.settings.compiler.cppstd:
            tc.variables["CMAKE_CXX_STANDARD"] = self._min_cppstd
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
        self._patch_sources()
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
        elif self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["pthread"]
        self.cpp_info.set_property("cmake_file_name", "PcapPlusPlus")
        self.cpp_info.set_property("cmake_target_name", "PcapPlusPlus::PcapPlusPlus")
