from conans import ConanFile, tools
import os

required_conan_version = ">=1.43.0"


class BackportCppRecipe(ConanFile):
    name = "backport-cpp"
    description = "An ongoing effort to bring modern C++ utilities to be compatible with C++11"
    topics = ("backport-cpp", "header-only", "backport")
    homepage = "https://github.com/bitwizeshift/BackportCpp"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source=True

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
        self.copy(os.path.join("include", "**", "*.hpp"), src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Backport")
        self.cpp_info.set_property("cmake_target_name", "Backport::Backport")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "Backport"
        self.cpp_info.names["cmake_find_package_multi"] = "Backport"
