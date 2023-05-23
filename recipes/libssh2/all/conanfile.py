from conans import ConanFile, CMake, tools
import functools
import os

required_conan_version = ">=1.43.0"


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

    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.12")
        if self.options.crypto_backend == "openssl":
            self.requires("openssl/1.1.1q")
        elif self.options.crypto_backend == "mbedtls":
            # libssh2/<=1.10.0 doesn't support mbedtls/3.x.x
            self.requires("mbedtls/2.25.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake)",
                              "list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake)")

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_ZLIB_COMPRESSION"] = self.options.with_zlib
        cmake.definitions["ENABLE_CRYPT_NONE"] = self.options.enable_crypt_none
        cmake.definitions["ENABLE_MAC_NONE"] = self.options.enable_mac_none
        cmake.definitions["ENABLE_DEBUG_LOGGING"] = self.options.enable_debug_logging
        if self.options.crypto_backend == "openssl":
            cmake.definitions["CRYPTO_BACKEND"] = "OpenSSL"
            cmake.definitions["OPENSSL_ROOT_DIR"] = self.deps_cpp_info["openssl"].rootpath
        elif self.options.crypto_backend == "mbedtls":
            cmake.definitions["CRYPTO_BACKEND"] = "mbedTLS"
        cmake.definitions["BUILD_EXAMPLES"] = False
        cmake.definitions["BUILD_TESTING"] = False
        # To install relocatable shared lib on Macos by default
        cmake.definitions["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        cmake.configure()
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Libssh2")
        self.cpp_info.set_property("cmake_target_name", "Libssh2::libssh2")
        self.cpp_info.set_property("pkg_config_name", "libssh2")
        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["_libssh2"].libs = tools.collect_libs(self)
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
