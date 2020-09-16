from conans import ConanFile, CMake, tools
import glob
import os


class LibreSSLConan(ConanFile):
    name = "libressl"
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
        self.copy("openssl/*.h", dst="include", src=libressl_include_dir)

        self.copy("*COPYING", dst="licenses", keep_path=False)
        if self.options.shared:
            self.copy("*.so*", dst="lib", symlinks=True, keep_path=False)
            self.copy("*.dylib", dst="lib", symlinks=True, keep_path=False)
            self.copy("*.dll", dst="bin", keep_path=False)
            self.copy("*.lib", dst="lib", keep_path=False)
            self.copy("*.dll.a", dst="lib", keep_path=False)
        else:
            self.copy("*.a", dst="lib", keep_path=False)
            self.copy("*.lib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "LibreSSL"
        self.cpp_info.names["cmake_find_package_multi"] = "LibreSSL"
        # Crypto
        self.cpp_info.components["crypto"].names["cmake_find_package"] = "Crypto"
        self.cpp_info.components["crypto"].names["cmake_find_package_multi"] = "Crypto"
        self.cpp_info.components["crypto"].names["pkg_config"] = "libcrypto"
        self.cpp_info.components["crypto"].libs = [self._lib_name("crypto")]
        if self.settings.os == "Linux":
            self.cpp_info.components["crypto"].system_libs = ["pthread", "rt"]
        elif self.settings.os == "SunOS":
            self.cpp_info.components["crypto"].system_libs = ["nsl", "socket"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["crypto"].system_libs = ["ws2_32"]
        # SSL
        self.cpp_info.components["ssl"].names["cmake_find_package"] = "SSL"
        self.cpp_info.components["ssl"].names["cmake_find_package_multi"] = "SSL"
        self.cpp_info.components["ssl"].names["pkg_config"] = "libssl"
        self.cpp_info.components["ssl"].libs = [self._lib_name("ssl")]
        self.cpp_info.components["ssl"].requires = ["crypto"]
        # TLS
        self.cpp_info.components["tls"].names["cmake_find_package"] = "TLS"
        self.cpp_info.components["tls"].names["cmake_find_package_multi"] = "TLS"
        self.cpp_info.components["tls"].names["pkg_config"] = "libtls"
        self.cpp_info.components["tls"].libs = [self._lib_name("tls")]
        self.cpp_info.components["tls"].requires = ["crypto", "ssl"]
        # openssl
        self.cpp_info.components["openssl"].names["pkg_config"] = "openssl"
        self.cpp_info.components["openssl"].requires = ["crypto", "ssl"]

    def _lib_name(self, name):
        if self.settings.os == "Windows" and tools.Version(self.version) >= "3.0.0":
            lib_fullpath = glob.glob(os.path.join(self.package_folder, "lib", "*{}*".format(name)))[0]
            lib_name = os.path.basename(lib_fullpath).split(".")[0].replace("lib", "")
            return lib_name
        return name
