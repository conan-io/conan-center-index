from conans import ConanFile, CMake, tools
from conans.tools import Version
from conans.errors import ConanInvalidConfiguration
import os


class IXWebSocketConan(ConanFile):
    name = "ixwebsocket"
    description = "IXWebSocket is a C++ library for WebSocket client and server development"
    topics = ("conan", "IXWebSocket", "socket", "websocket")

    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/machinezone/IXWebSocket"

    # License for the library
    license = "BSD-3-Clause"

    exports_sources = ["CMakeLists.txt"]

    settings = "os", "compiler", "build_type", "arch"

    short_paths = True
    generators = "cmake"

    options = {
        "tls": ["mbedtls", "openssl", "applessl", False],
        "fPIC": [True, False]
    }
    default_options = {k: v[0] for k, v in options.items()}

    def _can_use_openssl(self):
        if self.settings.os == "Windows":
            # Future: support for OpenSSL on Windows was introduced in 7.9.3. Earlier versions force MbedTLS
            return Version(self.version) >= "7.9.3"
        # The others do, by default, support OpenSSL and MbedTLS. Non-standard operating systems might
        # be a challenge.
        # Older versions doesn't support OpenSSL on Mac, but those are unlikely to be built now.
        return True

    def configure(self):
        if self.options.tls == "applessl" and not tools.is_apple_os(self.settings.os):
            raise ConanInvalidConfiguration("Can only use Apple SSL on Apple.")
        elif not self._can_use_openssl() and self.options.tls == "openssl":
            # Should maybe specify 7.9.3, even though it isn't packaged with conan?
            raise ConanInvalidConfiguration("This version doesn't support OpenSSL with Windows; use v9.1.9 or newer for this to be valid")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        self.requires("zlib/1.2.11")

        if not self.options.tls:
            # if we're not using TLS of some or another type, then no libraries after this
            # point are needed.
            return;

        # Invalid configurations have been eliminated by this point, so it should be safe
        # to add the dependencies without any further checks
        if self.options.tls == "openssl":
            self.requires("openssl/1.1.1e")
        elif self.options.tls == "mbedtls":
            self.requires("mbedtls/2.16.3-apache")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("IXWebSocket-" + self.version, "sources")

    def _configure_cmake(self):
        cmake = CMake(self)

        # User-selectable options
        cmake.definitions["USE_TLS"] = self.options.tls != False
        cmake.definitions["USE_MBED_TLS"] = self.options.tls == "mbedtls"
        cmake.definitions["USE_OPEN_SSL"] = self.options.tls == "openssl"
        # Apple configures itself

        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        # Include package license
        self.copy(pattern="LICENSE*", dst="licenses", src="sources")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            # possibly required for all configurations. It's linked in by the IXWebSocket CMake, anyway.
            self.cpp_info.system_libs.append("Ws2_32")
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        elif tools.is_apple_os(self.settings.os) and self.options.tls == "applessl":
            self.cpp_info.frameworks = ['Security', 'CoreFoundation']
