from conans import ConanFile, tools
import os

required_conan_version = ">=1.43.0"


class TlExpectedConan(ConanFile):
    name = "tl-expected"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://tl.tartanllama.xyz"
    description = "C++11/14/17 std::expected with functional-style extensions"
    topics = ("cpp11", "cpp14", "cpp17", "expected")
    license = "CC0-1.0"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, 11)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("*",
                  src=os.path.join(self._source_subfolder, "include"),
                  dst="include")
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "tl-expected")
        self.cpp_info.set_property("cmake_target_name", "tl::expected")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "tl-expected"
        self.cpp_info.filenames["cmake_find_package_multi"] = "tl-expected"
        self.cpp_info.names["cmake_find_package"] = "tl"
        self.cpp_info.names["cmake_find_package_multi"] = "tl"
        self.cpp_info.components["expected"].names["cmake_find_package"] = "expected"
        self.cpp_info.components["expected"].names["cmake_find_package_multi"] = "expected"
        self.cpp_info.components["expected"].set_property("cmake_target_name", "tl::expected")
