import os
from conans import ConanFile, tools

required_conan_version = ">=1.28.0"

class ScopeLiteConan(ConanFile):
    name = "scope-lite"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/martinmoene/scope-lite"
    description = "scope lite - A migration path to C++ library extensions scope_exit, scope_fail, \
                    scope_success, unique_resource in a single-file header-only library"
    topics = ("conan", "cpp98", "cpp11", "scope", "library extensions")
    license = "BSL-1.0"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "scope-lite"
        self.cpp_info.filenames["cmake_find_package_multi"] = "scope-lite"
        self.cpp_info.names["cmake_find_package"] = "nonstd"
        self.cpp_info.names["cmake_find_package_multi"] = "nonstd"
        self.cpp_info.components["scopelite"].names["cmake_find_package"] = "scope-lite"
        self.cpp_info.components["scopelite"].names["cmake_find_package_multi"] = "scope-lite"
