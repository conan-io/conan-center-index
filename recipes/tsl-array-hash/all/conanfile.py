from conans import ConanFile, tools
import os

required_conan_version = ">=1.28.0"

class TslArrayHashConan(ConanFile):
    name = "tsl-array-hash"
    license = "MIT"
    description = "C++ implementation of a fast and memory efficient hash map and hash set specialized for strings."
    topics = ("conan", "string", "structure", "hash map", "hash set")
    homepage = "https://github.com/Tessil/array-hash"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("array-hash-{}".format(self.version), self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "tsl-array-hash"
        self.cpp_info.filenames["cmake_find_package_multi"] = "tsl-array-hash"
        self.cpp_info.names["cmake_find_package"] = "tsl"
        self.cpp_info.names["cmake_find_package_multi"] = "tsl"
        self.cpp_info.components["array_hash"].names["cmake_find_package"] = "array_hash"
        self.cpp_info.components["array_hash"].names["cmake_find_package_multi"] = "array_hash"
