from conan import ConanFile, tools
import os

required_conan_version = ">=1.43.0"


class ScopeLiteConan(ConanFile):
    name = "scope-lite"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/martinmoene/scope-lite"
    description = "scope lite - A migration path to C++ library extensions scope_exit, scope_fail, \
                    scope_success, unique_resource in a single-file header-only library"
    topics = ("cpp98", "cpp11", "scope", "library extensions")
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
        self.cpp_info.set_property("cmake_file_name", "scope-lite")
        self.cpp_info.set_property("cmake_target_name", "nonstd::scope-lite")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "scope-lite"
        self.cpp_info.filenames["cmake_find_package_multi"] = "scope-lite"
        self.cpp_info.names["cmake_find_package"] = "nonstd"
        self.cpp_info.names["cmake_find_package_multi"] = "nonstd"
        self.cpp_info.components["scopelite"].names["cmake_find_package"] = "scope-lite"
        self.cpp_info.components["scopelite"].names["cmake_find_package_multi"] = "scope-lite"
        self.cpp_info.components["scopelite"].set_property("cmake_target_name", "nonstd::scope-lite")
