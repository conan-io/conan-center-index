from conans import ConanFile, CMake, tools
import os


class LibreSSLConan(ConanFile):
    name = "libressl"
    version = "2.9.2"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.libressl.org/"
    license = ("OpenSSL", "BSD", "ISC")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False}, {"fPIC": True}
    topics = ("SSL", "TLS", "openssl")
    description = "LibreSSL is a version of the TLS/crypto stack forked from OpenSSL in 2014, with goals of modernizing the codebase, improving security, and applying best practice development processes."
    generators = "cmake"

    @property
    def libressl_src(self):
        return "%s-%s" % (self.name, self.version)

    def config_options(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

    def build(self):
        # needed to properly overwrite MSVC runtime
        tools.replace_in_file(os.path.join(self.libressl_src, "CMakeLists.txt"), "project (LibreSSL C ASM)", """project (LibreSSL C ASM)
include(${CMAKE_CURRENT_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)""")

        # libressl adds a suffix to Windows dll names, which is really annoying for packaging
        tools.replace_in_file(os.path.join(self.libressl_src, "crypto", "CMakeLists.txt"), "set(CRYPTO_POSTFIX -${CRYPTO_MAJOR_VERSION})", "set(CRYPTO_POSTFIX)")
        tools.replace_in_file(os.path.join(self.libressl_src, "tls", "CMakeLists.txt"), "set(TLS_POSTFIX -${TLS_MAJOR_VERSION})", "set(TLS_POSTFIX)")
        tools.replace_in_file(os.path.join(self.libressl_src, "ssl", "CMakeLists.txt"), "set(SSL_POSTFIX -${SSL_MAJOR_VERSION})", "set(SSL_POSTFIX)")
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED"] = self.options.shared
        cmake.definitions["USE_SHARED"] = self.options.shared
        # LibreSSL's CMake install rules are a bit weird
        # explicitly remove CMAKE_INSTALL_PREFIX to avoid installing certs
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = ""
        cmake.definitions["LIBRESSL_APPS"] = "OFF"
        cmake.configure(source_dir=self.libressl_src)
        cmake.build()

    def package(self):
        libressl_include_dir = os.path.join(self.libressl_src, "include")
        self.copy("tls.h", dst="include", src=libressl_include_dir)
        self.copy("openssl/*", dst="include", src=libressl_include_dir)

        self.copy("*COPYING", dst="licenses", keep_path=False)
        if self.options.shared:
            self.copy("*.so*", dst="lib", symlinks=True, keep_path=False)
            self.copy("*.dylib", dst="lib", symlinks=True, keep_path=False)
            self.copy("*.dll", dst="bin", keep_path=False)
            # do not forget import libraries
            self.copy("*.lib", dst="lib", keep_path=False)
        else:
            self.copy("*.a", dst="lib", keep_path=False)
            self.copy("*.lib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["tls", "ssl", "crypto"]
        if self.settings.os == "Windows":
            self.cpp_info.libs.append("ws2_32")
            self.cpp_info.defines.append("NOCRYPT")
        elif self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
