import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir

required_conan_version = ">=2.0"


class LibratsConan(ConanFile):
    name = "librats"
    description = (
        "C++17 peer-to-peer networking library: encrypted P2P (Noise XX), "
        "DHT/mDNS discovery, NAT traversal (STUN/UPnP/NAT-PMP), GossipSub "
        "pub/sub, file transfer, optional BitTorrent."
    )
    # librats itself is MIT. It embeds adapted single-primitive crypto sources
    # and, for Android API < 24, a getifaddrs() shim, each keeping its own
    # notice; see THIRD_PARTY_NOTICES.md upstream. For non-Android targets the
    # BSD-2/1-Clause parts are not compiled and this reduces to MIT AND BSD-3-Clause.
    license = "MIT AND BSD-3-Clause AND BSD-2-Clause AND BSD-1-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/librats/librats"
    topics = ("p2p", "networking", "dht", "noise-protocol", "gossipsub", "bittorrent", "nat-traversal")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "set_target_properties(rats PROPERTIES POSITION_INDEPENDENT_CODE ON)",
                        "")

    def generate(self):
        tc = CMakeToolchain(self)
        # Library kind is driven by Conan's `shared` option.
        tc.cache_variables["RATS_SHARED_LIBRARY"] = bool(self.options.shared)
        tc.cache_variables["RATS_STATIC_LIBRARY"] = not bool(self.options.shared)
        tc.cache_variables["RATS_BUILD_TESTS"] = False
        tc.cache_variables["RATS_BUILD_CLIENT"] = False
        tc.cache_variables["RATS_BUILD_EXAMPLES"] = False
        tc.cache_variables["RATS_BINDINGS"] = True
        tc.cache_variables["RATS_SEARCH_FEATURES"] = False
        tc.cache_variables["RATS_STORAGE"] = False
        tc.cache_variables["RATS_INSTALL"] = True
        # The upstream CMakeLists derives the version from `git describe`;
        # a source tarball has no .git, so feed it explicitly.
        tc.cache_variables["RATS_VERSION_OVERRIDE"] = str(self.version)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        # Notices of the adapted third-party sources listed in THIRD_PARTY_NOTICES.md.
        copy(self, "*.LICENSE",
             src=os.path.join(self.source_folder, "licenses"),
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "rats")
        self.cpp_info.set_property("cmake_target_name", "rats::rats")
        self.cpp_info.libs = ["rats"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread", "atomic"]
        elif self.settings.os == "FreeBSD":
            self.cpp_info.system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "iphlpapi", "bcrypt", "advapi32"]
        elif self.settings.os == "Android":
            # Android NDK provides log/dl; threading is in libc.
            self.cpp_info.system_libs = ["log"]
