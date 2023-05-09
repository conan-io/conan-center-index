import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import (
    copy,
    get,
    replace_in_file,
    rm,
    rmdir,
)

required_conan_version = ">=1.53.0"


class LibTinsConan(ConanFile):
    name = "libtins"
    description = "High-level, multiplatform C++ network packet sniffing and crafting library."
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mfontanini/libtins"
    topics = (
        "pcap",
        "packets",
        "network",
        "packet-analyser",
        "packet-parsing",
        "libpcap",
        "sniffing",
    )
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ack_tracker": [True, False],
        "with_wpa2": [True, False],
        "with_dot11": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ack_tracker": True,
        "with_wpa2": True,
        "with_dot11": True,
    }

    @property
    def _min_cppstd(self):
        return 11

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libpcap/1.10.1", transitive_headers=True, transitive_libs=True)
        if self.options.with_ack_tracker:
            self.requires("boost/1.81.0", transitive_headers=True, transitive_libs=True)
        if self.options.with_wpa2:
            self.requires("openssl/3.1.0")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LIBTINS_BUILD_EXAMPLES"] = False
        tc.variables["LIBTINS_BUILD_TESTS"] = False
        tc.variables["LIBTINS_BUILD_SHARED"] = self.options.shared
        tc.variables["LIBTINS_ENABLE_CXX11"] = True
        tc.variables["LIBTINS_ENABLE_ACK_TRACKER"] = self.options.with_ack_tracker
        tc.variables["LIBTINS_ENABLE_WPA2"] = self.options.with_wpa2
        tc.variables["LIBTINS_ENABLE_DOT11"] = self.options.with_dot11
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        replace_in_file(
            self,
            os.path.join(self.source_folder, "CMakeLists.txt"),
            "FIND_PACKAGE(PCAP REQUIRED)",
            "find_package(libpcap REQUIRED)",
        )
        replace_in_file(
            self,
            os.path.join(self.source_folder, "src", "CMakeLists.txt"),
            "${PCAP_LIBRARY}",
            "libpcap::libpcap",
        )

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            pattern="LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "CMake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"), recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["tins"]
        self.cpp_info.set_property("pkg_config_name", "libtins")

        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.defines.append("TINS_STATIC")
            self.cpp_info.system_libs.extend(["ws2_32", "iphlpapi"])
