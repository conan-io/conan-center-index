import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.files import copy, get, rmdir, rm
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.53.0"

class UvgRTPConan(ConanFile):
    name = "uvgrtp"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ultravideo/uvgRTP"
    description = "uvgRTP is a Real-Time Transport Protocol (RTP) library written in C++ with a focus on simple-to-use and high-efficiency media delivery over the internet"
    topics = ("rtp", "networking", "streaming", "multimedia")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_crypto": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_crypto": True,
    }
    package_type = "library"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_crypto:
            self.requires("cryptopp/[>=8.7.0 <9]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # This library requires C++17
        self.settings.compiler.cppstd = "17"

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["UVGRTP_DISABLE_CRYPTO"] = not self.options.with_crypto
        tc.variables["UVGRTP_DISABLE_TESTS"] = True
        tc.variables["UVGRTP_DISABLE_EXAMPLES"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "packaging/License.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"), keep_path=False)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "uvgrtp")
        self.cpp_info.set_property("cmake_target_name", "uvgrtp::uvgrtp")

        self.cpp_info.libs = ["uvgrtp"]

        if self.options.with_crypto:
            self.cpp_info.requires = ["cryptopp::cryptopp"]

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["wsock32", "ws2_32"])

        if self.settings.os == "Macos":
            self.cpp_info.frameworks.append("Security")
