from conans import ConanFile, CMake, tools
import os


class IXWebSocketConan(ConanFile):
    name = "ixwebsocket"
    description = "WebSocket client/server"
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
        "use_vendored_third_party": [True, False],
        "use_ws": [False, True],
        "fPIC": [True, False]
    }
    default_options = {k: v[0] for k, v in options.items()}

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            self.default_options["use_mbed_tls"] = True

    def requirements(self):

        if(self.settings.os != "Windows" and self.settings.os != "Macos" and not self.options.use_mbed_tls and self.options.use_tls):
            # On Windows and Mac, the current CMake config prefers different SSL providers.
            # Specifically, Windows is forced to use MbedTLS, while Mac can use
            # MBEDTLS or an Apple-specific SSL provider. UNIX can use OpenSSL or MbedTLS
            # So even though both these operating systems support it, it isn't used.
            self.requires.add("openssl/1.1.1c")

        self.requires.add("zlib/1.2.11")

        if (self.options.use_mbed_tls and not self.options.use_tls):
            print("WARN: Attempting to use mbed tls without enabling TLS.")

        if not self.options.use_vendored_third_party and (self.settings.os == "Windows" and self.options.use_tls or self.options.use_mbed_tls):
            self.requires.add("mbedtls/2.6.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("IXWebSocket-" + self.version, "sources")

    def addLibrary(self, keyBase, includeName, cmake, plural=False):
        cmake.definitions[keyBase +
                          "_LIBRARY"] = self.deps_cpp_info[includeName].rootpath
        includePath = keyBase + "_INCLUDE_DIR"
        if plural == True:
            includePath += "S"
        cmake.definitions[includePath] = os.path.join(
            self.deps_cpp_info[includeName].rootpath, self.deps_cpp_info[includeName].includedirs[0])

    def configure_cmake(self):
        cmake = CMake(self)

        # User-selectable options
        cmake.definitions["USE_TLS"] = self.options.use_tls
        cmake.definitions["USE_MBED_TLS"] = self.options.use_mbed_tls
        cmake.definitions["USE_WS"] = self.options.use_ws
        cmake.definitions["USE_VENDORED_THIRD_PARTY"] = self.options.use_vendored_third_party

        # Library linking
        if (self.options.use_tls and not self.options.use_mbed_tls and not self.settings.os == "Windows" and not self.settings.os == "Macos"):
            os.environ['OPENSSL_ROOT_DIR'] = self.deps_cpp_info["OpenSSL"].rootpath
        self.addLibrary("ZLIB", "zlib", cmake)
        if not self.options.use_vendored_third_party and (self.options.use_mbed_tls or self.options.use_tls and self.settings.os == "Windows"):
            self.addLibrary("MBEDTLS", "mbedtls", cmake, True)
            self.addLibrary("MBEDCRYPTO", "mbedtls", cmake, True)
            self.addLibrary("MBEDX509", "mbedtls", cmake, True)
        cmake.configure()
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()
        cmake.install()

    def package(self):
        # Include package license
        self.copy("license*", dst="licenses", src="sources")

        # Include binaries and headers
        self.copy("*.h", dst="include", src="include")
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.options.use_tls and self.settings.os == "Windows":
            # Include linking with the websocket
            self.cpp_info.libs += ["Ws2_32"]
        if self.options.use_tls and (self.options.use_mbed_tls and self.options.use_vendored_third_party or self.settings.os == "Windows"):
            # This doesn't really affect MSVC builds, but it might if the compiler changes in the future.
            if "mbedtls" not in self.cpp_info.libs:
                self.cpp_info.libs += ["mbedtls", "mbedx509", "mbedcrypto"]
            else:
                pIdx = self.cpp_info.libs.index("mbedtls")
                cIdx = self.cpp_info.libs.index("mbedcrypto")
                xIdx = self.cpp_info.libs.index("mbedx509")
                # Linking order matters on some compilers. Aside MSVC, Clang and GCC, and potentially others, require the linking
                # order of -lmbedtls -l mbedx509 -lmbedcrypto, as outlined in the README for mbedTLS.
                # See also: https://stackoverflow.com/a/17741992/6296561
                if (cIdx > pIdx or xIdx > pIdx or cIdx > xIdx):
                    self.cpp_info.libs = [
                        x for x in self.cpp_info.libs if "mbed" not in x] + ["mbedtls", "mbedx509", "mbedcrypto"]

        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
