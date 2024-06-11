import os

from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, get, rmdir, replace_in_file

required_conan_version = ">=1.53.0"


class CoseCConan(ConanFile):
    name = "cose-c"
    description = "Implementation of COSE in C using cn-cbor and openssl"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cose-wg/COSE-C"
    topics = "cbor"
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def requirements(self):
        self.requires("cn-cbor/1.0.0", transitive_headers=True)

        if self.options.with_ssl == "mbedtls":
            self.requires("mbedtls/2.16.12", transitive_headers=True)
        else:
            self.requires("openssl/[>=1.1 <4]", transitive_headers=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.cache_variables["COSE_C_COVERALLS"] = False
        tc.cache_variables["COSE_C_BUILD_TESTS"] = False
        tc.cache_variables["COSE_C_BUILD_DOCS"] = False
        tc.cache_variables["COSE_C_BUILD_DUMPER"] = False
        tc.cache_variables["COSE_C_USE_MBEDTLS"] = self.options.with_ssl == "mbedtls"
        tc.cache_variables["COSE_C_USE_FIND_PACKAGE"] = True
        tc.cache_variables["COSE_C_EXPORT_TARGETS"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.set_property("openssl", "cmake_file_name", "OPENSSL")
        deps.set_property("mbedtls", "cmake_target_name", "mbedtls")
        deps.generate()

    def _patch_sources(self):
        # For ${OPENSSL_LIBRARIES} and ${OPENSSL_INCLUDE_DIR}
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "OpenSSL", "OPENSSL")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "secur32", "crypt32", "bcrypt"])
        if is_apple_os(self):
            self.cpp_info.frameworks.extend(["CoreFoundation", "Security"])
        if self.options.with_ssl == "mbedtls":
            self.cpp_info.defines.append("COSE_C_USE_MBEDTLS")
        else:
            self.cpp_info.defines.append("COSE_C_USE_OPENSSL")
