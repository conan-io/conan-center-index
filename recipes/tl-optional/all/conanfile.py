from conans import ConanFile, tools
import os

required_conan_version = ">=1.28.0"

class TlOptionalConan(ConanFile):
    name = "tl-optional"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://tl.tartanllama.xyz"
    description = "C++11/14/17 std::optional with functional-style extensions and reference support"
    topics = ("cpp11", "cpp14", "cpp17", "optional")
    license = "CC0-1.0"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "optional-" + self.version
        os.rename(extracted_folder, self._source_subfolder)

    def package(self):
        self.copy("*",
                  src=os.path.join(self._source_subfolder, "include"),
                  dst="include")
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "tl-optional"
        self.cpp_info.filenames["cmake_find_package_multi"] = "tl-optional"
        self.cpp_info.names["cmake_find_package"] = "tl"
        self.cpp_info.names["cmake_find_package_multi"] = "tl"
        self.cpp_info.components["optional"].names["cmake_find_package"] = "optional"
        self.cpp_info.components["optional"].names["cmake_find_package_multi"] = "optional"
