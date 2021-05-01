from conans import ConanFile, tools
import os

required_conan_version = ">=1.28.0"

class TslOrderedMapConan(ConanFile):
    name = "tsl-ordered-map"
    license = "MIT"
    description = "C++ hash map and hash set which preserve the order of insertion."
    topics = ("conan", "ordered-map", "structure", "hash map", "hash set")
    homepage = "https://github.com/Tessil/ordered-map"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("ordered-map-{}".format(self.version), self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "tsl-ordered-map"
        self.cpp_info.filenames["cmake_find_package_multi"] = "tsl-ordered-map"
        self.cpp_info.names["cmake_find_package"] = "tsl"
        self.cpp_info.names["cmake_find_package_multi"] = "tsl"
        self.cpp_info.components["ordered_map"].names["cmake_find_package"] = "ordered_map"
        self.cpp_info.components["ordered_map"].names["cmake_find_package_multi"] = "ordered_map"
