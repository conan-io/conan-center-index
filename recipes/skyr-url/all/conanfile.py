from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
import os


class SkyrUrlConan(ConanFile):
    name = "skyr-url"
    homepage = "https://cpp-netlib.github.io/url"
    description = "A C++ library that implements the WhatWG URL specification"
    topics = ("conan", "whatwg", "url", "parser")
    url = "https://github.com/conan-io/conan-center-index"
    license = "Boost"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], "with_json": [True, False]}
    default_options = {'shared': False, 'fPIC': True, 'with_json': True}
    exports_sources = "CMakeLists.txt"
    generators = "cmake_find_package_multi"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder (self):
        return "build_subfolder"

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        # https://github.com/cpp-netlib/url#requirements
        return {
            "Visual Studio": "15",
            "gcc": "7",
            "clang": "5",
            "apple-clang": "10",
        }

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(
            str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires C++17 support. The current compiler {} {} does not support it.".format(
                    self.name, self.settings.compiler, self.settings.compiler.version))

    def requirements(self):
        self.requires("tl-expected/1.0.0")
        self.requires("range-v3/0.10.0")
        if self.options.with_json:
            self.requires("nlohmann_json/3.8.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "url-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["skyr_BUILD_TESTS"] = "OFF"
        self._cmake.definitions["skyr_FULL_WARNINGS"] = "OFF"
        self._cmake.definitions["skyr_WARNINGS_AS_ERRORS"] = "OFF"
        self._cmake.definitions["skyr_USE_STATIC_CRT"] = not self.options.shared
        self._cmake.definitions["skyr_ENABLE_JSON_FUNCTIONS"] = not self.options.with_json
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_id(self):
        pass
