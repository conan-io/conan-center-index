from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
import os


class crc32cConan(ConanFile):
    name = "crc32c"
    description = "CRC32C implementation with support for CPU-specific acceleration instructions"
    topics = ("conan", "crc32c", "crc")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/crc32c"
    license = "BSD-3-Clause"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
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

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake is not None:
            return self._cmake

        self._cmake = CMake(self)
        if not self.settings.compiler.cppstd:
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
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
    
    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Crc32c"
        self.cpp_info.names["cmake_find_package_multi"] = "Crc32c"

        self.cpp_info.components["_crc32c"].names["cmake_find_package"] = "crc32c"
        self.cpp_info.components["_crc32c"].names["cmake_find_package_multi"] = "crc32c"
        self.cpp_info.components["_crc32c"].libs = ["crc32c"]
