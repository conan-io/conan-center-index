from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class CocoyaxiConan(ConanFile):
    name = "cocoyaxi"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/idealvin/cocoyaxi"
    license = "MIT"
    description = "A go-style coroutine library in C++11 and more."
    topics = ("cocoyaxi", "coroutine", "c++11")
    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libcurl": [True, False],
        "with_openssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libcurl": False,
        "with_openssl": False,
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
        if self.options.with_libcurl:
            self.requires("libcurl/7.80.0")
        if self.options.with_libcurl or self.options.with_openssl:
            self.requires("openssl/1.1.1m")

    def build_requirements(self):
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            #  The OSX_ARCHITECTURES target property is now respected for the ASM language
            self.build_requires("cmake/3.20.1")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
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
        runtime = self.settings.get_safe("compiler.runtime")
        if runtime:
            self._cmake.definitions["STATIC_VS_CRT"] = "MT" in runtime
        self._cmake.definitions["WITH_LIBCURL"] = self.options.with_libcurl
        self._cmake.definitions["WITH_OPENSSL"] = self.options.with_openssl
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "cocoyaxi")
        self.cpp_info.set_property("cmake_target_name", "cocoyaxi::co")
        self.cpp_info.names["cmake_find_package"] = "cocoyaxi"
        self.cpp_info.names["cmake_find_package_multi"] = "cocoyaxi"
        self.cpp_info.components["co"].names["cmake_find_package"] = "co"
        self.cpp_info.components["co"].names["cmake_find_package_multi"] = "co"
        self.cpp_info.components["co"].set_property("cmake_target_name", "cocoyaxi::co")
        self.cpp_info.components["co"].libs = ["co"]

    def validate(self):
        if self.options.with_libcurl:
            if not self.options.with_openssl:
                raise ConanInvalidConfiguration(f"{self.name} requires with_openssl=True when using with_libcurl=True")
            if self.options["libcurl"].with_ssl != "openssl":
                raise ConanInvalidConfiguration(f"{self.name} requires libcurl:with_ssl='openssl' to be enabled")
            if not self.options["libcurl"].with_zlib:
                raise ConanInvalidConfiguration(f"{self.name} requires libcurl:with_zlib=True to be enabled")
