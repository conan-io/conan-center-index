from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.microsoft import is_msvc_static_runtime
import os


required_conan_version = ">=2.4.0"


class MsQuicConan(ConanFile):
    name = "msquic"
    package_type = "static-library"
    license = ("MIT", "Apache-2.0")
    url = "https://github.com/conan-io/conan-center-index"
    description = "Cross-platform, C implementation of the IETF QUIC protocol"
    homepage = "https://github.com/microsoft/msquic"
    topics = ("quic", "networking", "protocol", "microsoft", "ietf")
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}
    implements = ["auto_shared_fpic"]
    languages = "C", "C++"

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        for submodule_name, submodule_data in self.conan_data["submodules"][self.version].items():
            get(self, **submodule_data, strip_root=True, destination=os.path.join(self.source_folder, "submodules", submodule_name))

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.20]")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["QUIC_BUILD_TOOLS"] = False
        tc.cache_variables["QUIC_BUILD_TEST"] = False
        tc.cache_variables["QUIC_BUILD_PERF"] = False
        tc.cache_variables["QUIC_BUILD_SHARED"] = False
        # Upstream defaults both to ON and then overwrites CMAKE_MSVC_RUNTIME_LIBRARY
        # after project(), which forces /MT even when compiler.runtime is dynamic.
        # PARTIAL implies STATIC, so it must stay off for /MD to take effect.
        tc.cache_variables["QUIC_STATIC_LINK_CRT"] = is_msvc_static_runtime(self)
        tc.cache_variables["QUIC_STATIC_LINK_PARTIAL_CRT"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"),
             excludes="submodules/*")
        copy(self, "LICENSE.txt", src=os.path.join(self.source_folder, "submodules", "quictls"),
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE", src=os.path.join(self.source_folder, "submodules", "xdp-for-windows"),
             dst=os.path.join(self.package_folder, "licenses", "xdp-for-windows"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["msquic"]
        self.cpp_info.defines = ["QUIC_BUILD_STATIC"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "dl", "m"]
            self.cpp_info.defines.append("CX_PLATFORM_LINUX")
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks = ["CoreFoundation", "Security"]
            self.cpp_info.defines.append("CX_PLATFORM_DARWIN")
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = [
                "ws2_32", "schannel", "ntdll", "bcrypt", "ncrypt", "crypt32",
                "iphlpapi", "advapi32", "secur32", "wbemuuid", "winmm", "onecore",
            ]
