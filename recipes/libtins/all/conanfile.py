import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir
from conan.errors import ConanException
from conan.tools.scm import Version

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
        "with_tcp_stream_custom_data": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ack_tracker": True,
        "with_wpa2": True,
        "with_dot11": True,
        "with_tcp_stream_custom_data": True,
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
        # pcap.h is largely imported in public headers: tins/packet_writer.h, tins/sniffer.h
        self.requires("libpcap/1.10.5", transitive_headers=True)
        if self.options.with_ack_tracker or self.options.with_tcp_stream_custom_data:
            # Used in two public headers:
            # - https://github.com/mfontanini/libtins/blob/v4.4/include/tins/tcp_ip/ack_tracker.h#L38
            # - https://github.com/mfontanini/libtins/blob/v4.4/include/tins/tcp_ip/stream.h#L48
            self.requires("boost/1.83.0", transitive_headers=True)
        if self.options.with_wpa2:
            self.requires("openssl/[>=1.1 <4]")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["LIBTINS_BUILD_EXAMPLES"] = False
        tc.cache_variables["LIBTINS_BUILD_TESTS"] = False
        tc.cache_variables["LIBTINS_BUILD_SHARED"] = self.options.shared
        tc.cache_variables["LIBTINS_ENABLE_CXX11"] = True
        tc.cache_variables["LIBTINS_ENABLE_ACK_TRACKER"] = self.options.with_ack_tracker
        tc.cache_variables["LIBTINS_ENABLE_TCP_STREAM_CUSTOM_DATA"] = self.options.with_tcp_stream_custom_data
        tc.cache_variables["LIBTINS_ENABLE_WPA2"] = self.options.with_wpa2
        tc.cache_variables["LIBTINS_ENABLE_DOT11"] = self.options.with_dot11
        tc.cache_variables["PCAP_LIBRARY"] = "libpcap::libpcap"
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"
        if Version(self.version) > "4.5":
            raise ConanException("CMAKE_POLICY_VERSION_MINIMUM hardcoded to 3.5, please, check if new version supports CMake 4.")
        tc.generate()
        deps = CMakeDeps(self)
        deps.set_property("libpcap", "cmake_file_name", "PCAP")
        deps.generate()

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

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.defines.append("TINS_STATIC")
            self.cpp_info.system_libs.extend(["ws2_32", "iphlpapi"])
        if self.options.with_tcp_stream_custom_data:
            self.cpp_info.defines.append("TINS_HAVE_TCP_STREAM_CUSTOM_DATA")
        if self.options.with_ack_tracker:
            self.cpp_info.defines.append("TINS_HAVE_ACK_TRACKER")
