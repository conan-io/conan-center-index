import os

from conans import ConanFile, CMake, tools

class CpphttplibConan(ConanFile):
    name = "cpp-httplib"
    description = "A C++11 single-file header-only cross platform HTTP/HTTPS library."
    license = "MIT"
    topics = ("conan", "cpp-httplib", "http", "https", "header-only")
    homepage = "https://github.com/yhirose/cpp-httplib"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os"
    options = {"with_openssl": [True, False], "with_zlib": [True, False]}
    default_options = {"with_openssl": False, "with_zlib": False}
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if self.options.with_openssl:
            self.requires.add("openssl/1.1.1d")
        if self.options.with_zlib:
            self.requires.add("zlib/1.2.11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = CMake(self)
        cmake.configure()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        if self.options.with_openssl:
            self.cpp_info.defines("CPPHTTPLIB_OPENSSL_SUPPORT")
        if self.options.with_zlib:
            self.cpp_info.defines("CPPHTTPLIB_ZLIB_SUPPORT")
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        self.cpp_info.includedirs = ["include", os.path.join("include", "httplib")]
