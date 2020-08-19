from conans import ConanFile, tools
import os

required_conan_version = ">=1.28.0"

class TslRobinMapConan(ConanFile):
    name = "tsl-robin-map"
    license = "MIT"
    description = "C++ implementation of a fast hash map and hash set using robin hood hashing."
    topics = ("conan", "robin-map", "structure", "hash map", "hash set")
    homepage = "https://github.com/Tessil/robin-map"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("robin-map-{}".format(self.version), self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "tsl-robin-map"
        self.cpp_info.filenames["cmake_find_package_multi"] = "tsl-robin-map"
        self.cpp_info.names["cmake_find_package"] = "tsl"
        self.cpp_info.names["cmake_find_package_multi"] = "tsl"
        self.cpp_info.components["robin_map"].names["cmake_find_package"] = "robin_map"
        self.cpp_info.components["robin_map"].names["cmake_find_package_multi"] = "robin_map"
