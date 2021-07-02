from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class IXWebSocketConan(ConanFile):
    name = "ixwebsocket"
    description = "IXWebSocket is a C++ library for WebSocket client and server development"
    topics = ("conan", "IXWebSocket", "socket", "websocket")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/machinezone/IXWebSocket"
    license = "BSD-3-Clause"
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "compiler", "build_type", "arch"
    short_paths = True
    generators = "cmake"
    options = {
        "fPIC": [True, False],
        "tls": ["mbedtls", "openssl", "applessl", False],
        "with_zlib": [True, False]
    }
    default_options = {
        "fPIC": True,
        "tls": "mbedtls",
        "with_zlib": True
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if tools.Version(self.version) < "10.1.5":
            # zlib is always required before 10.1.5
            del self.options.with_zlib

    def _can_use_openssl(self):
        if self.settings.os == "Windows":
            # Future: support for OpenSSL on Windows was introduced in 7.9.3. Earlier versions force MbedTLS
            return tools.Version(self.version) >= "7.9.3"
        # The others do, by default, support OpenSSL and MbedTLS. Non-standard operating systems might
        # be a challenge.
        # Older versions doesn't support OpenSSL on Mac, but those are unlikely to be built now.
        return True

    def configure(self):
        if self.settings.compiler.cppstd:
            # After version 11.0.8, IXWebSocket is fully compatible with C++ 11. https://github.com/machinezone/IXWebSocket/commit/ee5a2eb46ee0e109415dc02b0db85a9c76256090
            tools.check_min_cppstd(self, 14 if tools.Version(self.version) < "11.0.8" else 11)
        if self.options.tls == "applessl" and not tools.is_apple_os(self.settings.os):
            raise ConanInvalidConfiguration("Can only use Apple SSL on Apple.")
        elif not self._can_use_openssl() and self.options.tls == "openssl":
            raise ConanInvalidConfiguration("This version doesn't support OpenSSL with Windows; use v7.9.3 or newer for this to be valid")

    def requirements(self):
        if self.options.get_safe("with_zlib", True):
            self.requires("zlib/1.2.11")
        if self.options.tls == "openssl":
            self.requires("openssl/1.1.1j")
        elif self.options.tls == "mbedtls":
            self.requires("mbedtls/2.16.3-apache")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("IXWebSocket-" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["USE_TLS"] = bool(self.options.tls)
        self._cmake.definitions["USE_MBED_TLS"] = self.options.tls == "mbedtls"
        self._cmake.definitions["USE_OPEN_SSL"] = self.options.tls == "openssl"
        # Apple configures itself if USE_TLS True, and USE_MBED_TLS + USE_OPEN_SSL False
        if tools.Version(self.version) >= "10.1.5":
            self._cmake.definitions["USE_ZLIB"] = self.options.with_zlib

        self._cmake.configure()
        return self._cmake

    def build(self):
        if tools.Version(self.version) >= "9.5.7":
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                                  "set(CMAKE_POSITION_INDEPENDENT_CODE ON)", "")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE*", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["wsock32", "ws2_32", "shlwapi"])
            if bool(self.options.tls):
                self.cpp_info.system_libs.append("Crypt32")
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        if self.options.get_safe("with_zlib", False):
            self.cpp_info.defines.append("IXWEBSOCKET_USE_ZLIB")
        if self.options.tls == "mbedtls":
            self.cpp_info.defines.append("IXWEBSOCKET_USE_MBED_TLS")
        elif self.options.tls == "openssl":
            self.cpp_info.defines.append("IXWEBSOCKET_USE_OPEN_SSL")
        elif self.options.tls == "applessl":
            self.cpp_info.frameworks = ["Security", "CoreFoundation"]
            self.cpp_info.defines.append("IXWEBSOCKET_USE_SECURE_TRANSPORT")
