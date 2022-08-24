from conans import ConanFile, tools
import os

required_conan_version = ">=1.43.0"


class OptionalLiteConan(ConanFile):
    name = "optional-lite"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/martinmoene/optional-lite"
    description = "A single-file header-only version of a C++17-like optional, a nullable object for C++98, C++11 and later"
    topics = ("cpp98", "cpp17", "optional", "optional-implementations")
    license = "BSL-1.0"
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
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "optional-lite")
        self.cpp_info.set_property("cmake_target_name", "nonstd::optional-lite")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "optional-lite"
        self.cpp_info.filenames["cmake_find_package_multi"] = "optional-lite"
        self.cpp_info.names["cmake_find_package"] = "nonstd"
        self.cpp_info.names["cmake_find_package_multi"] = "nonstd"
        self.cpp_info.components["optionallite"].names["cmake_find_package"] = "optional-lite"
        self.cpp_info.components["optionallite"].names["cmake_find_package_multi"] = "optional-lite"
        self.cpp_info.components["optionallite"].set_property("cmake_target_name", "nonstd::optional-lite")
