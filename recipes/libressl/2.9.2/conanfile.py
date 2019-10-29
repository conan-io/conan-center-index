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
    default_options = {"shared": False, "fPIC": True}
    exports_sources = "CMakeLists.txt"
    topics = ("SSL", "TLS", "openssl")
    description = ("LibreSSL is a version of the TLS/crypto stack forked from OpenSSL in 2014, "
                   "with goals of modernizing the codebase, improving security, and applying "
                   "best practice development processes.")
    generators = "cmake"
    _source_subfolder = "source_subfolder"


    def config_options(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED"] = self.options.shared
        cmake.definitions["USE_SHARED"] = self.options.shared
        # LibreSSL's CMake install rules are a bit weird
        # explicitly remove CMAKE_INSTALL_PREFIX to avoid defining OPENSSLDIR
        # as </absolute/path/to/package_folder/etc/ssl>
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = ""
        cmake.definitions["LIBRESSL_APPS"] = "OFF"
        cmake.configure()
        cmake.build()

    def package(self):
        libressl_include_dir = os.path.join(self._source_subfolder, "include")
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
        # LibreSSL adds a version number as a suffix to each library on Windows
        if self.settings.os != "Windows":
            self.cpp_info.libs = ["tls", "ssl", "crypto"]
            if self.settings.os == "Linux":
                self.cpp_info.libs.append("pthread")
        else:
            # On MinGW, the link order of libraries matter
            libs = tools.collect_libs(self)
            libs.sort(reverse=True)
            self.cpp_info.libs = libs
            self.cpp_info.libs.append("ws2_32")
            self.cpp_info.defines.append("NOCRYPT")
