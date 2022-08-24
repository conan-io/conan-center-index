import os
from conans import CMake, ConanFile, tools

required_conan_version = ">=1.33.0"


class LibCuckooConan(ConanFile):
    name = "libcuckoo"
    description = "A high-performance, concurrent hash table"
    license = "Apache-2.0"
    homepage = "https://github.com/efficient/libcuckoo"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("concurrency", "hashmap", "header-only", "library", "cuckoo")
    settings = "arch", "build_type", "compiler", "os"
    generators = "cmake", "cmake_find_package_multi"
    no_copy_source = True

    @property
    def _minimum_cpp_standard(self):
        return 11

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        # Install with CMake
        cmake = CMake(self)
        cmake.definitions["BUILD_EXAMPLES"] = "OFF"
        cmake.definitions["BUILD_STRESS_TESTS"] = "OFF"
        cmake.definitions["BUILD_TESTS"] = "OFF"
        cmake.definitions["BUILD_UNIT_TESTS"] = "OFF"
        cmake.definitions["BUILD_UNIVERSAL_BENCHMARK"] = "OFF"
        cmake.configure(source_folder=self._source_subfolder)
        cmake.install()
        # Copy license files
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        # Remove CMake config files (only files in share)
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
        self.cpp_info.names["cmake_find_package"] = "libcuckoo"
        self.cpp_info.names["cmake_find_package_multi"] = "libcuckoo"
