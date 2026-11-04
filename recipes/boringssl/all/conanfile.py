from conan import ConanFile
from conan.tools.build import check_min_cppstd, check_min_cstd, stdcpp_library
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, replace_in_file
import os

required_conan_version = ">=2.4"


class BoringSSLConan(ConanFile):
    name = "boringssl"
    description = "BoringSSL is a fork of OpenSSL aimed at Google needs."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://boringssl.googlesource.com/boringssl/"
    topics = ("tls", "ssl", "crypto", "openssl", "boringssl")
    package_type = "library"
    languages = ("C", "C++")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    provides = "openssl"
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.22]")

        if self.settings.os == "Windows" and str(self.settings.arch) in ("x86", "x86_64"):
            self.tool_requires("nasm/2.16.01")

    def validate_build(self):
        # BoringSSL requires C++17 when building, but public interface is C
        check_min_cppstd(self, 17)

    def validate(self):
        if self.settings.get_safe("compiler.cstd"):
            check_min_cstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][str(self.version)], strip_root=True)
        # INFO: Let Conan manage the C++ standard from settings.compiler.cppstd
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "set(CMAKE_CXX_STANDARD",
                        "# set(CMAKE_CXX_STANDARD")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_TESTING"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenSSL")

        self.cpp_info.components["crypto"].set_property("cmake_target_name", "OpenSSL::Crypto")
        self.cpp_info.components["crypto"].libs = ["crypto"]
        if self.options.shared:
            self.cpp_info.components["crypto"].defines = ["BORINGSSL_SHARED_LIBRARY"]
        elif stdcpp_library(self):
            self.cpp_info.components["crypto"].system_libs.append(stdcpp_library(self))
        if self.settings.os == "Windows":
            self.cpp_info.components["crypto"].system_libs = ["ws2_32"]
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["crypto"].system_libs = ["pthread"]

        self.cpp_info.components["ssl"].set_property("cmake_target_name", "OpenSSL::SSL")
        self.cpp_info.components["ssl"].libs = ["ssl"]
        self.cpp_info.components["ssl"].requires = ["crypto"]
        if self.options.shared:
            self.cpp_info.components["ssl"].defines = ["BORINGSSL_SHARED_LIBRARY"]
        elif stdcpp_library(self):
            self.cpp_info.components["ssl"].system_libs.append(stdcpp_library(self))
