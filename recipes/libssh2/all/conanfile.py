from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


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
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zlib": True,
        "enable_crypt_none": False,
        "enable_mac_none": False,
        "crypto_backend": "openssl",
    }

    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

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
            self.requires("zlib/1.2.11")
        if self.options.crypto_backend == "openssl":
            self.requires("openssl/1.1.1l")
        elif self.options.crypto_backend == "mbedtls":
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

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_ZLIB_COMPRESSION"] = self.options.with_zlib
        self._cmake.definitions["ENABLE_CRYPT_NONE"] = self.options.enable_crypt_none
        self._cmake.definitions["ENABLE_MAC_NONE"] = self.options.enable_mac_none
        if self.options.crypto_backend == "openssl":
            self._cmake.definitions["CRYPTO_BACKEND"] = "OpenSSL"
            self._cmake.definitions["OPENSSL_ROOT_DIR"] = self.deps_cpp_info["openssl"].rootpath
        elif self.options.crypto_backend == "mbedtls":
            self._cmake.definitions["CRYPTO_BACKEND"] = "mbedTLS"
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.configure()
        return self._cmake

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
        self.cpp_info.names["cmake_find_package"] = "Libssh2"
        self.cpp_info.names["cmake_find_package_multi"] = "Libssh2"
        self.cpp_info.names["pkg_config"] = "libssh2"
        self.cpp_info.components["_libssh2"].names["cmake_find_package"] = "libssh2"
        self.cpp_info.components["_libssh2"].names["cmake_find_package_multi"] = "libssh2"
        self.cpp_info.components["_libssh2"].names["pkg_config"] = "libssh2"
        self.cpp_info.components["_libssh2"].libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.components["_libssh2"].system_libs.append("ws2_32")
        elif self.settings.os == "Linux":
            self.cpp_info.components["_libssh2"].system_libs.extend(["pthread", "dl"])
        if self.options.with_zlib:
            self.cpp_info.components["_libssh2"].requires.append("zlib::zlib")
        if self.options.crypto_backend == "openssl":
            self.cpp_info.components["_libssh2"].requires.append("openssl::openssl")
        elif self.options.crypto_backend == "mbedtls":
            self.cpp_info.components["_libssh2"].requires.append("mbedtls::mbedtls")
