from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class SymengineConan(ConanFile):
    name = "symengine"
    description = "A fast symbolic manipulation library, written in C++"
    license = "MIT"
    topics = ("symbolic", "algebra")
    homepage = "https://symengine.org/"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    short_paths = True
    requires = "boost/1.76.0"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(
            **self.conan_data["sources"][self.version],
            strip_root=True,
            destination=self._source_subfolder,
        )

    def _configure_cmake(self):
        if self._cmake is None:
            self._cmake = CMake(self)
            self._cmake.definitions["BUILD_TESTS"] = False
            self._cmake.definitions["BUILD_BENCHMARKS"] = False
            self._cmake.definitions["INTEGER_CLASS"] = "boostmp"
            self._cmake.definitions["MSVC_USE_MT"] = False
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # [CMAKE-MODULES-CONFIG-FILES (KB-H016)]
        tools.remove_files_by_mask(self.package_folder, "*.cmake")
        # [DEFAULT PACKAGE LAYOUT (KB-H013)]
        if self.settings.os == "Windows":
            tools.rmdir(os.path.join(self.package_folder, "CMake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.names["cmake_find_package"] = "symengine"
        self.cpp_info.names["cmake_find_package_multi"] = "symengine"
