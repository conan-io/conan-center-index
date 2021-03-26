from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.28.0"

class SkyrUrlConan(ConanFile):
    name = "skyr-url"
    homepage = "https://cpp-netlib.github.io/url"
    description = "A C++ library that implements the WhatWG URL specification"
    topics = ("conan", "whatwg", "url", "parser")
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSL-1.0"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], "with_json": [True, False], "with_fs": [True, False]}
    default_options = {"shared": False, "fPIC": True, "with_json": True, "with_fs": True}
    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package_multi"
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
        # https://github.com/cpp-netlib/url/tree/v1.12.0#requirements
        return {
            "Visual Studio": "16",
            "gcc": "7",
            "clang": "6" if tools.Version(self.version) <= "1.12.0" else "8",
            "apple-clang": "10",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires C++17 support. The current compiler {} {} does not support it.".format(
                    self.name, self.settings.compiler, self.settings.compiler.version))

        if self.options.with_fs and self.settings.compiler == "apple-clang":
            raise ConanInvalidConfiguration("apple-clang currently does not support with filesystem")

        if self.options.shared:
            # https://github.com/cpp-netlib/url/blob/dd345361ed86e4c1cabfe94743a8e769b346840c/src/CMakeLists.txt#L17
            raise ConanInvalidConfiguration("shared is currently not supported by upstream")

        if tools.Version(self.version) >= "1.13.0" and not self.settings.compiler == "Visual Studio":
            # There's tedious compilation errors in C3i against ranges-v3
            raise ConanInvalidConfiguration("{}/{} with {} is currently not supported".format(self.name, self.version, self.settings.compiler))

    def requirements(self):
        self.requires("tl-expected/1.0.0")
        self.requires("range-v3/0.11.0")
        if self.options.with_json:
            self.requires("nlohmann_json/3.9.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "url-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["skyr_BUILD_TESTS"] = False
        self._cmake.definitions["skyr_FULL_WARNINGS"] = False
        self._cmake.definitions["skyr_WARNINGS_AS_ERRORS"] = False
        self._cmake.definitions["skyr_ENABLE_JSON_FUNCTIONS"] = self.options.with_json
        self._cmake.definitions["skyr_ENABLE_FILESYSTEM_FUNCTIONS"] = self.options.with_fs
        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["skyr_USE_STATIC_CRT"] = "MT" in self.settings.compiler.runtime
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE_1_0.txt", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "skyr-url"
        self.cpp_info.filenames["cmake_find_package_multi"] = "skyr-url"
        self.cpp_info.names["cmake_find_package"] = "skyr"
        self.cpp_info.names["cmake_find_package_multi"] = "skyr"
        self.cpp_info.components["url"].name = "skyr-url"
        self.cpp_info.components["url"].libs = tools.collect_libs(self)
        self.cpp_info.components["url"].requires = ["tl-expected::tl-expected", "range-v3::range-v3" ]
        if self.options.with_json:
            self.cpp_info.components["url"].requires.append("nlohmann_json::nlohmann_json")
