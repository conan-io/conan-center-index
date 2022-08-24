from conan import ConanFile, tools
from conans import CMake
import os

required_conan_version = ">=1.43.0"


class crc32cConan(ConanFile):
    name = "crc32c"
    description = "CRC32C implementation with support for CPU-specific acceleration instructions"
    topics = ("crc32c", "crc")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/crc32c"
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

    exports_sources = "CMakeLists.txt"
    generators = "cmake"
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

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        if not tools.valid_min_cppstd(self, 11):
            self._cmake.definitions["CMAKE_CXX_STANDARD"] = 11
        self._cmake.definitions["CRC32C_BUILD_TESTS"] = False
        self._cmake.definitions["CRC32C_BUILD_BENCHMARKS"] = False
        self._cmake.definitions["CRC32C_INSTALL"] = True
        self._cmake.definitions["CRC32C_USE_GLOG"] = False

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Crc32c")
        self.cpp_info.set_property("cmake_target_name", "Crc32c::crc32c")

        # TODO: back to global scope once cmake_find_package* generators removed
        self.cpp_info.components["_crc32c"].libs = ["crc32c"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "Crc32c"
        self.cpp_info.names["cmake_find_package_multi"] = "Crc32c"
        self.cpp_info.components["_crc32c"].names["cmake_find_package"] = "crc32c"
        self.cpp_info.components["_crc32c"].names["cmake_find_package_multi"] = "crc32c"
        self.cpp_info.components["_crc32c"].set_property("cmake_target_name", "Crc32c::crc32c")
