from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
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
        "use_openssl": [False, True],
        "use_vendored_third_party": [True, False],
        "use_ws": [False, True],
        "fPIC": [True, False]
    }
    default_options = {k: v[0] for k, v in options.items()}

    def intVersion(self):
        return int(self.version.replace(".", ""))

    def canUseOpenSSL(self):
        if self.settings.os == "Windows":
            # Future: support for OpenSSL was introduced in 7.9.3. Earlier versions force MbedTLS
            return False if self.intVersion() < 793 else True
        # The others do, by default, support OpenSSL and MbedTLS. Non-standard operating systems might
        # be a challenge.
        return True 

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            self.default_options["use_mbed_tls"] = True
            if not self.canUseOpenSSL():
                del self.options.use_openssl
        elif self.settings.os == "Linux":
            # On Linux, if TLS is enabled and mbed is disabled, the only option is OpenSSL.
            del self.options.use_openssl

    def requirements(self):
        if self.options.use_mbed_tls == True and self.options.use_tls == False:
            raise ConanInvalidConfiguration("TLS must be enabled to use mbedtls")
        elif self.options.use_mbed_tls == True and "use_openssl" in self.options and self.options["use_openssl"] == True:
            raise ConanInvalidConfiguration("Cannot use both OpenSSL and MbedTLS")

        if(self.canUseOpenSSL() and not self.options.use_mbed_tls and self.options.use_tls 
                                and ("use_openssl" not in self.options or self.options.use_openssl == True)):    
            self.requires.add("openssl/1.1.1c")

        self.requires.add("zlib/1.2.11")

        if not self.options.use_vendored_third_party and (self.settings.os == "Windows" and self.options.use_tls 
                                                          and not self.canUseOpenSSL() or self.options.use_mbed_tls):
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
            os.environ['OPENSSL_ROOT_DIR'] = self.deps_cpp_info["openssl"].rootpath
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
        self.copy("LICENSE.txt", dst="licenses", src="sources")

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
            self.cpp_info.system_libs.append("Ws2_32")
        if self.options.use_tls and (self.options.use_mbed_tls and self.options.use_vendored_third_party or self.settings.os == "Windows"):
            # This doesn't really affect MSVC builds, but it might if the compiler changes in the future.
            if "mbedtls" not in self.cpp_info.libs:
                self.cpp_info.libs.extend(["mbedtls", "mbedx509", "mbedcrypto"])
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
            self.cpp_info.system_libs.append("pthread")

        if self.options.use_tls and self.settings.os == "Macos" and not self.options.use_openssl and not self.options.use_mbed_tls:
            # Required
             self.cpp_info.frameworks = [ 'Security', 'CoreFoundation' ]
