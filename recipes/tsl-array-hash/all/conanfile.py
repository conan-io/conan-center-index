from conan import ConanFile, tools$
import os

required_conan_version = ">=1.43.0"


class TslArrayHashConan(ConanFile):
    name = "tsl-array-hash"
    license = "MIT"
    description = "C++ implementation of a fast and memory efficient hash map and hash set specialized for strings."
    topics = ("string", "structure", "hash map", "hash set")
    homepage = "https://github.com/Tessil/array-hash"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "tsl-array-hash")
        self.cpp_info.set_property("cmake_target_name", "tsl::array_hash")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "tsl-array-hash"
        self.cpp_info.filenames["cmake_find_package_multi"] = "tsl-array-hash"
        self.cpp_info.names["cmake_find_package"] = "tsl"
        self.cpp_info.names["cmake_find_package_multi"] = "tsl"
        self.cpp_info.components["array_hash"].names["cmake_find_package"] = "array_hash"
        self.cpp_info.components["array_hash"].names["cmake_find_package_multi"] = "array_hash"
        self.cpp_info.components["array_hash"].set_property("cmake_target_name", "tsl::array_hash")
