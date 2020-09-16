from conans import ConanFile, CMake, tools
import glob
import os


class LibreSSLConan(ConanFile):
    name = "libressl"
    provides = "openssl"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.libressl.org/"
    license = ("OpenSSL", "BSD", "ISC")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    topics = ("SSL", "TLS", "openssl")
    description = ("LibreSSL is a version of the TLS/crypto stack forked from OpenSSL in 2014, "
                   "with goals of modernizing the codebase, improving security, and applying "
                   "best practice development processes.")

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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["LIBRESSL_SKIP_INSTALL"] = False
        self._cmake.definitions["LIBRESSL_APPS"] = False # Warning: if enabled, do not use cmake installation, to avoid installing files in OPENSSLDIR
        self._cmake.definitions["LIBRESSL_TESTS"] = False
        self._cmake.definitions["ENABLE_ASM"] = True
        self._cmake.definitions["ENABLE_EXTRATESTS"] = False
        self._cmake.definitions["ENABLE_NC"] = False
        self._cmake.definitions["OPENSSLDIR"] = "C:/Windows/libressl/ssl" if self.settings.os == "Windows" else "/etc/ssl"
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("*COPYING", dst="licenses", keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()
        for cmake_file in glob.glob(os.path.join(self.package_folder, "include", "*.cmake")):
            os.remove(cmake_file)
        tools.rmdir(os.path.join(self.package_folder, "include", "CMakeFiles"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

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
        libressl_version = tools.Version(self.version)
        if self.settings.os == "Windows" and \
           (libressl_version >= "3.1.0" or (libressl_version < "3.1.0" and self.options.shared)):
            lib_fullpath = glob.glob(os.path.join(self.package_folder, "lib", "*{}*".format(name)))[0]
            lib_name = os.path.basename(lib_fullpath).split(".")[0].replace("lib", "")
            return lib_name
        return name
