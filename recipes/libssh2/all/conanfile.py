from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get, replace_in_file, rmdir
import os

required_conan_version = ">=1.52.0"


class Libssh2Conan(ConanFile):
    name = "libssh2"
    description = "libssh2 is a client-side C library implementing the SSH2 protocol"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libssh2.org"
    topics = ("libssh", "ssh", "shell", "ssh2", "connection")
    license = "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zlib": [True, False],
        "enable_crypt_none": [True, False],
        "enable_mac_none": [True, False],
        "crypto_backend": ["openssl", "mbedtls"],
        "enable_debug_logging": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zlib": True,
        "enable_crypt_none": False,
        "enable_mac_none": False,
        "crypto_backend": "openssl",
        "enable_debug_logging": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.13")
        if self.options.crypto_backend == "openssl":
            self.requires("openssl/1.1.1q")
        elif self.options.crypto_backend == "mbedtls":
            # libssh2/<=1.10.0 doesn't support mbedtls/3.x.x
            self.requires("mbedtls/2.25.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_ZLIB_COMPRESSION"] = self.options.with_zlib
        tc.variables["ENABLE_CRYPT_NONE"] = self.options.enable_crypt_none
        tc.variables["ENABLE_MAC_NONE"] = self.options.enable_mac_none
        tc.variables["ENABLE_DEBUG_LOGGING"] = self.options.enable_debug_logging
        if self.options.crypto_backend == "openssl":
            tc.variables["CRYPTO_BACKEND"] = "OpenSSL"
            tc.variables["OPENSSL_ROOT_DIR"] = self.dependencies["openssl"].package_folder.replace("\\", "/")
        elif self.options.crypto_backend == "mbedtls":
            tc.variables["CRYPTO_BACKEND"] = "mbedTLS"
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_TESTING"] = False
        # To install relocatable shared lib on Macos by default
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                              "set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake)",
                              "list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake)")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Libssh2")
        self.cpp_info.set_property("cmake_target_name", "Libssh2::libssh2")
        self.cpp_info.set_property("pkg_config_name", "libssh2")
        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["_libssh2"].libs = collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.components["_libssh2"].system_libs.append("ws2_32")
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_libssh2"].system_libs.extend(["pthread", "dl"])

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "Libssh2"
        self.cpp_info.names["cmake_find_package_multi"] = "Libssh2"
        self.cpp_info.components["_libssh2"].names["cmake_find_package"] = "libssh2"
        self.cpp_info.components["_libssh2"].names["cmake_find_package_multi"] = "libssh2"
        self.cpp_info.components["_libssh2"].set_property("cmake_target_name", "Libssh2::libssh2")
        self.cpp_info.components["_libssh2"].set_property("pkg_config_name", "libssh2")
        if self.options.with_zlib:
            self.cpp_info.components["_libssh2"].requires.append("zlib::zlib")
        if self.options.crypto_backend == "openssl":
            self.cpp_info.components["_libssh2"].requires.append("openssl::openssl")
        elif self.options.crypto_backend == "mbedtls":
            self.cpp_info.components["_libssh2"].requires.append("mbedtls::mbedtls")
