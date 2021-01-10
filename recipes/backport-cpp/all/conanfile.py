import os

from conans import ConanFile, tools


class BackportCppRecipe(ConanFile):
    name = "backport-cpp"
    description = "An ongoing effort to bring modern C++ utilities to be compatible with C++11"
    topics = ("conan", "backport-cpp", "header-only", "backport")
    homepage = "https://github.com/bitwizeshift/BackportCpp"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    no_copy_source=True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "BackportCpp-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(os.path.join("include", "**", "*.hpp"), src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Backport"
        self.cpp_info.names["cmake_find_package_multi"] = "Backport"
