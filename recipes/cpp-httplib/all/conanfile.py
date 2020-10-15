import os

from conans import ConanFile, tools

class CpphttplibConan(ConanFile):
    name = "cpp-httplib"
    description = "A C++11 single-file header-only cross platform HTTP/HTTPS library."
    license = "MIT"
    topics = ("conan", "cpp-httplib", "http", "https", "header-only")
    homepage = "https://github.com/yhirose/cpp-httplib"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True
    settings = "os", "compiler"
    options = {
        "with_openssl": [True, False],
        "with_zlib": [True, False],
        "with_brotli": [True, False]
    }
    default_options = {
        "with_openssl": False,
        "with_zlib": False,
        "with_brotli": False
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if tools.Version(self.version) < "0.7.2":
            del self.options.with_brotli

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.1h")
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.get_safe("with_brotli"):
            self.requires("brotli/1.0.9")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("httplib.h", dst=os.path.join("include", "httplib"), src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "httplib"
        self.cpp_info.names["cmake_find_package_multi"] = "httplib"
        if self.options.with_openssl:
            self.cpp_info.defines.append("CPPHTTPLIB_OPENSSL_SUPPORT")
        if self.options.with_zlib:
            self.cpp_info.defines.append("CPPHTTPLIB_ZLIB_SUPPORT")
        if self.options.get_safe("with_brotli"):
            self.cpp_info.defines.append("CPPHTTPLIB_BROTLI_SUPPORT")
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["crypt32", "cryptui", "ws2_32"]
        self.cpp_info.includedirs = ["include", os.path.join("include", "httplib")]
