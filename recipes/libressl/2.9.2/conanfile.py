from conans import ConanFile, CMake, tools
import os


class LibreSSLConan(ConanFile):
    name = "libressl"
    version = "2.9.2"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.libressl.org/"
    license = "OpenSSL - OpenBSD"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
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
