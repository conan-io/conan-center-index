from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import copy, get, rmdir
import os


required_conan_version = ">=2.4.0"


class MsQuicConan(ConanFile):
    name = "msquic"
    package_type = "static-library"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Cross-platform, C implementation of the IETF QUIC protocol"
    homepage = "https://github.com/microsoft/msquic"
    topics = ("quic", "networking", "protocol", "microsoft", "ietf")
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}
    implements = ["auto_shared_fpic"]
    languages = "C"

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
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["msquic"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "dl", "m"]
            self.cpp_info.defines = ["CX_PLATFORM_LINUX"]
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks = ["CoreFoundation", "Security"]
            self.cpp_info.defines = ["CX_PLATFORM_DARWIN"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "schannel", "ntdll", "bcrypt", "ncrypt", "crypt32", "iphlpapi", "advapi32", "secur32"]
