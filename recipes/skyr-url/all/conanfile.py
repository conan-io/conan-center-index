from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os
import functools

required_conan_version = ">=1.45.0"

class SkyrUrlConan(ConanFile):
    name = "skyr-url"
    description = "A C++ library that implements the WhatWG URL specification"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://cpp-netlib.github.io/url"
    topics = ("whatwg", "url", "parser")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_json": [True, False],
        "with_fs": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_json": True,
        "with_fs": True,
    }
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

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
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
        if self.settings.compiler.get_safe("libcxx") == "libstdc++":
            raise ConanInvalidConfiguration("{} supports only libstdc++'s new ABI".format(self.name))

    def requirements(self):
        self.requires("tl-expected/1.0.0")
        self.requires("range-v3/0.12.0")
        if self.options.with_json:
            self.requires("nlohmann_json/3.10.5")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["skyr_BUILD_TESTS"] = False
        cmake.definitions["skyr_FULL_WARNINGS"] = False
        cmake.definitions["skyr_WARNINGS_AS_ERRORS"] = False
        cmake.definitions["skyr_ENABLE_JSON_FUNCTIONS"] = self.options.with_json
        cmake.definitions["skyr_ENABLE_FILESYSTEM_FUNCTIONS"] = self.options.with_fs
        if is_msvc(self):
            cmake.definitions["skyr_USE_STATIC_CRT"] = is_msvc_static_runtime(self)
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE_1_0.txt", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "skyr-url")
        self.cpp_info.set_property("cmake_target_name", "skyr::skyr-url")

        self.cpp_info.components["url"].name = "skyr-url"
        self.cpp_info.components["url"].libs = tools.collect_libs(self)
        self.cpp_info.components["url"].requires = ["tl-expected::tl-expected", "range-v3::range-v3"]
        if self.options.with_json:
            self.cpp_info.components["url"].requires.append("nlohmann_json::nlohmann_json")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["url"].system_libs.append("m")

        self.cpp_info.filenames["cmake_find_package"] = "skyr-url"
        self.cpp_info.filenames["cmake_find_package_multi"] = "skyr-url"
        self.cpp_info.names["cmake_find_package"] = "skyr"
        self.cpp_info.names["cmake_find_package_multi"] = "skyr"
