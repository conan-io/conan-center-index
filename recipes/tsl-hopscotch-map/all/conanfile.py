from conans import ConanFile, tools
import os

required_conan_version = ">=1.43.0"


class TslHopscotchMapConan(ConanFile):
    name = "tsl-hopscotch-map"
    license = "MIT"
    description = "C++ implementation of a fast hash map and hash set using hopscotch hashing"
    topics = ("structure", "hash map", "hash set")
    homepage = "https://github.com/Tessil/hopscotch-map"
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
        self.cpp_info.set_property("cmake_file_name", "tsl-hopscotch-map")
        self.cpp_info.set_property("cmake_target_name", "tsl::hopscotch_map")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "tsl-hopscotch-map"
        self.cpp_info.filenames["cmake_find_package_multi"] = "tsl-hopscotch-map"
        self.cpp_info.names["cmake_find_package"] = "tsl"
        self.cpp_info.names["cmake_find_package_multi"] = "tsl"
        self.cpp_info.components["hopscotch_map"].names["cmake_find_package"] = "hopscotch_map"
        self.cpp_info.components["hopscotch_map"].names["cmake_find_package_multi"] = "hopscotch_map"
        self.cpp_info.components["hopscotch_map"].set_property("cmake_target_name", "tsl::hopscotch_map")
