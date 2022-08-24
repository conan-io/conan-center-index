from conan import ConanFile, tools
from conans import CMake
import os

required_conan_version = ">=1.43.0"


class SnappyConan(ConanFile):
    name = "snappy"
    description = "A fast compressor/decompressor"
    topics = ("snappy", "google", "compressor", "decompressor")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/snappy"
    license = "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["SNAPPY_BUILD_TESTS"] = False
        if tools.Version(self.version) >= "1.1.8":
            self._cmake.definitions["SNAPPY_FUZZING_BUILD"] = False
            self._cmake.definitions["SNAPPY_REQUIRE_AVX"] = False
            self._cmake.definitions["SNAPPY_REQUIRE_AVX2"] = False
            self._cmake.definitions["SNAPPY_INSTALL"] = True
        if tools.Version(self.version) >= "1.1.9":
            self._cmake.definitions["SNAPPY_BUILD_BENCHMARKS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Snappy")
        self.cpp_info.set_property("cmake_target_name", "Snappy::snappy")
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["snappylib"].libs = ["snappy"]
        if not self.options.shared and tools.stdcpp_library(self):
            self.cpp_info.components["snappylib"].system_libs.append(tools.stdcpp_library(self))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "Snappy"
        self.cpp_info.names["cmake_find_package_multi"] = "Snappy"
        self.cpp_info.components["snappylib"].names["cmake_find_package"] = "snappy"
        self.cpp_info.components["snappylib"].names["cmake_find_package_multi"] = "snappy"
        self.cpp_info.components["snappylib"].set_property("cmake_target_name", "Snappy::snappy")
