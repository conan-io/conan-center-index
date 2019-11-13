import os
from conans import ConanFile, CMake, tools

class Rangev3Conan(ConanFile):
    name = "range-v3"
    license = "BSL-1.0"
    homepage = "https://github.com/ericniebler/range-v3"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Experimental range library for C++11/14/17"
    topics = ("range", "range-library", "proposal", "iterator")
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = self.name + "-" + self.version
        os.rename(extracted_folder, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["RANGE_V3_TESTS"] = "OFF"
        cmake.definitions["RANGE_V3_EXAMPLES"] = "OFF"
        cmake.definitions["RANGE_V3_PERF"] = "OFF"
        cmake.definitions["RANGE_V3_DOCS"] = "OFF"
        cmake.definitions["RANGE_V3_HEADER_CHECKS"] = "OFF"
        cmake.configure()
        return cmake

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
