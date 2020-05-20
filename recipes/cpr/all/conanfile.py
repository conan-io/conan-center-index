from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class CprConan(ConanFile):
    name = "cpr"
    description = "C++ Requests: Curl for People, a spiritual port of Python Requests"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://whoshuu.github.io/cpr/"
    license = "MIT"
    topics = ("conan", "cpr", "requests", "web", "curl")
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": True,
    }
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.options.with_openssl:
            # If using OpenSSL, we need it to be active in libcurl too
            if self.options["libcurl"].with_openssl == False:  # 'is False' doesn't work here (see conan-io/conan#3620)
                raise ConanInvalidConfiguration("libcurl must be built with openssl support")
            self.options["libcurl"].with_openssl = True

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("cpr-{}".format(self.version), self._source_subfolder)

    def requirements(self):
        self.requires("libcurl/7.67.0")
        if self.options.with_openssl:
            self.output.warn("OpenSSL support is not stable yet. whoshuu/cpr#31")

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["USE_SYSTEM_CURL"] = True
        cmake.definitions["BUILD_CPR_TESTS"] = False
        cmake.definitions["GENERATE_COVERAGE"] = False
        cmake.definitions["USE_SYSTEM_GTEST"] = False
        cmake.definitions["CMAKE_USE_OPENSSL"] = self.options.with_openssl
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio" and self.options.shared:
            cmake.definitions["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["cpr"]
