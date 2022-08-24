from conan import ConanFile, tools$
import os

required_conan_version = ">=1.43.1"


class StatusValueLiteConan(ConanFile):
    name = "status-value-lite"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/martinmoene/status-value-lite"
    description = "status-value - A class for status and optional value for C++11 and later, C++98 variant provided in a single-file header-only library"
    topics = ("cpp98", "cpp11", "cpp14", "cpp17", "status_value", "status_value-implementations")
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
        self.cpp_info.set_property("cmake_file_name", "status-value-lite")
        self.cpp_info.set_property("cmake_target_name", "nonstd::status-value-lite")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "status-value-lite"
        self.cpp_info.filenames["cmake_find_package_multi"] = "status-value-lite"
        self.cpp_info.names["cmake_find_package"] = "nonstd"
        self.cpp_info.names["cmake_find_package_multi"] = "nonstd"
        self.cpp_info.components["status_valuelite"].names["cmake_find_package"] = "status-value-lite"
        self.cpp_info.components["status_valuelite"].names["cmake_find_package_multi"] = "status-value-lite"
        self.cpp_info.components["status_valuelite"].set_property("cmake_target_name", "nonstd::status-value-lite")
