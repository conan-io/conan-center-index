import os
from conans import ConanFile, CMake, tools


class EffceeConan(ConanFile):
    name = "effcee"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/effcee/"
    description = "Zstandard - Fast real-time compression algorithm"
    topics = ("conan", "effcee", "strings", "algorithm", "matcher")
    license = "Apache-2.0"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package_multi"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "14")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["EFFCEE_BUILD_TESTING"] = False
        self._cmake.definitions["EFFCEE_BUILD_SAMPLES"] = False
        self._cmake.definitions["RE2_BUILD_TESTING"] = False
        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["EFFCEE_ENABLE_SHARED_CRT"] = (self.settings.compiler.runtime in ["MD", "MDd"])

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def requirements(self):
        self.requires('re2/20210601')

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
