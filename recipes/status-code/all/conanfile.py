import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conans import tools

required_conan_version = ">=1.45.0"

class StatusCodeConan(ConanFile):
    name = "status-code"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ned14/status-code"
    description = "Proposed SG14 status_code for the C++ standard"
    topics = ("header-only", "proposal")
    settings = "os", "arch", "build_type", "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _compiler_required_cpp17(self):
        return {
            # Their README says gcc 5, but in testing only >=7 worked
            "gcc": "7",
            "clang": "3.3",
            "Visual Studio": "14",
            "apple-clang": "5",
        }

    def validate(self):
        try:
            minimum_required_compiler_version = self._compiler_required_cpp17[str(self.settings.compiler)]
            if tools.Version(self.settings.compiler.version) < minimum_required_compiler_version:
                raise ConanInvalidConfiguration("This package requires c++11 support. The current compiler does not support it.")
        except KeyError:
            self.output.warn("This recipe has no support for the current compiler. Please consider adding it.")

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
