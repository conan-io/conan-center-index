from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
import os

required_conan_version = ">=1.54.0"


class CoseCConan(ConanFile):
    name = "cose-c"
    license = "BSD-3-Clause"
    homepage = "https://github.com/cose-wg/COSE-C"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Implementation of COSE in C using cn-cbor and openssl"
    topics = ("cbor")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ssl": ["openssl", "mbedtls"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssl": "openssl",
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cn-cbor/1.0.0")
        if self.options.with_ssl == "mbedtls":
            self.requires("mbedtls/2.25.0")
        else:
            self.requires("openssl/1.1.1s")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["COSE_C_COVERALLS"] = False
        tc.variables["COSE_C_BUILD_TESTS"] = False
        tc.variables["COSE_C_BUILD_DOCS"] = False
        tc.variables["COSE_C_BUILD_DUMPER"] = False
        tc.variables["COSE_C_USE_MBEDTLS"] = self.options.with_ssl == "mbedtls"
        tc.variables["COSE_C_USE_FIND_PACKAGE"] = True
        tc.variables["COSE_C_EXPORT_TARGETS"] = True
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "cose-c")
        self.cpp_info.set_property("cmake_target_name", "cose-c::cose-c")
        self.cpp_info.libs = ["cose-c"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "secur32", "crypt32", "bcrypt"])
        elif is_apple_os(self):
            self.cpp_info.frameworks.extend(["CoreFoundation", "Security"])
