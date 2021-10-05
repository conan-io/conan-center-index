import os
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.33.0"


class CoConan(ConanFile):
    name = "co"
    description = "A go-style coroutine library in C++11 and more."
    topics = ("conan", "co", "coroutine", "c++11")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/idealvin/co"
    license = "MIT"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libcurl": [True, False],
        "with_openssl": [True, False],
        "static_vs_crt": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libcurl": False,
        "with_openssl": False,
        "static_vs_crt": True,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        if not self.options.shared:
            self._cmake.definitions["FPIC"] = self.options.fPIC
        self._cmake.definitions["STATIC_VS_CRT"] = self.options.static_vs_crt
        self._cmake.definitions["WITH_LIBCURL"] = self.options.with_libcurl
        self._cmake.definitions["WITH_OPENSSL"] = self.options.with_openssl
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.names["cmake_find_package"] = "CO"
        self.cpp_info.names["cmake_find_package_multi"] = "CO"
