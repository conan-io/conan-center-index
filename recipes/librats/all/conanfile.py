import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.tools.scm import Version

required_conan_version = ">=2.0"


class LibratsConan(ConanFile):
    name = "librats"
    description = (
        "C++17 peer-to-peer networking library: encrypted P2P (Noise XX), "
        "DHT/mDNS discovery, NAT traversal (STUN/UPnP/NAT-PMP), GossipSub "
        "pub/sub, file transfer, optional BitTorrent."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/librats/librats"
    topics = ("p2p", "networking", "dht", "noise-protocol", "gossipsub", "nat-traversal")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "search_features": [True, False],   # BitTorrent subsystem
        "storage": [True, False],           # distributed key/value store
        "bindings": [True, False],          # C ABI (rats_*)
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "search_features": False,
        "storage": False,
        "bindings": True,
    }
    implements = ["auto_shared_fpic"]

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12",
            "msvc": "192",
        }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not fully support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # Library kind is driven by Conan's `shared` option.
        tc.cache_variables["RATS_SHARED_LIBRARY"] = bool(self.options.shared)
        tc.cache_variables["RATS_STATIC_LIBRARY"] = not bool(self.options.shared)
        tc.cache_variables["RATS_BUILD_TESTS"] = False
        tc.cache_variables["RATS_BUILD_CLIENT"] = False
        tc.cache_variables["RATS_BUILD_EXAMPLES"] = False
        tc.cache_variables["RATS_BINDINGS"] = bool(self.options.bindings)
        tc.cache_variables["RATS_SEARCH_FEATURES"] = bool(self.options.search_features)
        tc.cache_variables["RATS_STORAGE"] = bool(self.options.storage)
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
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "rats")
        self.cpp_info.set_property("cmake_target_name", "rats::rats")
        self.cpp_info.libs = ["rats"]
        # Headers are installed as a tree under include/librats and are included
        # as "node/node.h", "subsystems/pubsub.h", ... The crypto/ directory is a
        # second root: security headers include "noise.h" unqualified. This
        # mirrors the upstream exported CMake target's INSTALL_INTERFACE.
        self.cpp_info.includedirs = ["include/librats", "include/librats/crypto"]

        if self.options.search_features:
            self.cpp_info.defines.append("RATS_SEARCH_FEATURES")
        if self.options.storage:
            self.cpp_info.defines.append("RATS_STORAGE")
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines.append("RATS_IMPORT_DLL")

        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "iphlpapi", "bcrypt"]
        elif self.settings.os == "Android":
            self.cpp_info.system_libs = ["log"]
