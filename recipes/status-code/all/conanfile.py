import os
from conan import ConanFile
from conans import tools

required_conan_version = ">=1.45.0"

class StatusCodeConan(ConanFile):
    name = "status-code"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ned14/status-code"
    description = "Proposed SG14 status_code for the C++ standard"
    topics = ("header-only", "proposal")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("Licence.txt", dst="licenses", src=self._source_subfolder)
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("*.ipp", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "status-code")
        self.cpp_info.set_property("cmake_target_name", "status-code::hl")

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.filenames["cmake_find_package"] = "status-code"
        self.cpp_info.filenames["cmake_find_package_multi"] = "status-code"
        self.cpp_info.names["cmake_find_package"] = "status-code::hl"
        self.cpp_info.names["cmake_find_package_multi"] = "status-code::hl"
