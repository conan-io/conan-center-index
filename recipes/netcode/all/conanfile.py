import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.tools.microsoft import is_msvc

required_conan_version = ">=2.19.0"


class NetcodeConan(ConanFile):
    name = "netcode"
    description = "A protocol for secure client/server connections over UDP"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mas-bandwidth/netcode"
    topics = ("udp", "networking", "games", "security", "client-server")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # Plain C library: the C++ standard/runtime settings do not affect the binary.
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # netcode bundles an amalgamated libsodium subset, but NETCODE_SYSTEM_SODIUM=ON
        # links an external one instead so the bundled copy is never compiled. Keeping
        # libsodium unvendored is deliberate: a vendored crypto copy inside this package
        # would not receive libsodium security updates through Conan.
        self.requires("libsodium/1.0.20")

    def validate(self):
        # netcode.h has no dllexport/dllimport decoration, so an MSVC shared build
        # exports no symbols and produces no import library to link against.
        if self.options.shared and is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.ref} cannot be built as a shared library with MSVC")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # Link the libsodium supplied by Conan rather than netcode's bundled subset.
        # Upstream locates it with find_path/find_library, which the toolchain's
        # CMAKE_INCLUDE_PATH/CMAKE_LIBRARY_PATH point at the Conan package.
        tc.cache_variables["NETCODE_SYSTEM_SODIUM"] = True
        # Tests and examples default ON in a top-level build.
        tc.cache_variables["NETCODE_BUILD_TESTS"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENCE", self.source_folder,
             os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["netcode"]
        if self.settings.os == "Windows":
            # Matches upstream's PUBLIC link interface. Qwave (QoS packet tagging,
            # MSVC-only) is not listed here: netcode.c pulls it in through a
            # #pragma comment(lib) that MSVC propagates from the library's objects.
            self.cpp_info.system_libs = ["ws2_32", "iphlpapi"]

