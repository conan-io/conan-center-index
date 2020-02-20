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
        "use_mbed_tls": [False, True],
        "use_tls": [True, False],
        "use_openssl": [False, True],
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
        if self.options.use_mbed_tls and not self.options.use_tls or self.options.get_safe("use_openssl") and not self.options.use_tls:
            raise ConanInvalidConfiguration("TLS must be enabled to use mbedtls")
        elif self.options.use_mbed_tls and self.options.get_safe("use_openssl"):
            raise ConanInvalidConfiguration("Cannot use both OpenSSL and MbedTLS")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            self.default_options["use_mbed_tls"] = True
            if not self._can_use_openssl():
                del self.options.use_openssl
        elif self.settings.os == "Linux":
            # On Linux, if TLS is enabled and mbed is disabled, the only option is OpenSSL.
            del self.options.use_openssl

    def requirements(self):

        if(self._can_use_openssl() and not self.options.use_mbed_tls and self.options.use_tls
           and (self.options.get_safe("use_openssl") or self.settings.os == "Linux")):
            self.requires.add("openssl/1.1.1c")

        self.requires.add("zlib/1.2.11")

        if self.settings.os == "Windows" and self.options.use_tls and not self._can_use_openssl() or self.options.use_mbed_tls:
            self.requires.add("mbedtls/2.16.3-apache")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("IXWebSocket-" + self.version, "sources")

    def _configure_cmake(self):
        cmake = CMake(self)

        # User-selectable options
        cmake.definitions["USE_TLS"] = self.options.use_tls
        cmake.definitions["USE_MBED_TLS"] = self.options.use_mbed_tls

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
        if self.options.use_tls and not self.options.use_mbed_tls and not self.options.get_safe("use_openssl") and self.settings.os == "Windows":
            # Include linking with the websocket
            self.cpp_info.system_libs.append("Ws2_32")

        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")

        if self.options.use_tls and self.settings.os == "Macos" and not self.options.use_openssl and not self.options.use_mbed_tls:
            # Required
            self.cpp_info.frameworks = ['Security', 'CoreFoundation']
