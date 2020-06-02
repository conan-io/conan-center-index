import os

from conans import ConanFile, tools

class CpphttplibConan(ConanFile):
    name = "cpp-httplib"
    description = "A C++11 single-file header-only cross platform HTTP/HTTPS library."
    license = "MIT"
    topics = ("conan", "cpp-httplib", "http", "https", "header-only")
    homepage = "https://github.com/yhirose/cpp-httplib"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os"
    options = {"with_openssl": [True, False], "with_zlib": [True, False]}
    default_options = {"with_openssl": False, "with_zlib": False}
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.1g")
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("httplib.h", dst=os.path.join("include", "httplib"), src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        if self.options.with_openssl:
            self.cpp_info.defines.append("CPPHTTPLIB_OPENSSL_SUPPORT")
        if self.options.with_zlib:
            self.cpp_info.defines.append("CPPHTTPLIB_ZLIB_SUPPORT")
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        self.cpp_info.includedirs = ["include", os.path.join("include", "httplib")]
