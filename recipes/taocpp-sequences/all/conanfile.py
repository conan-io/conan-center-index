import os
from conans import ConanFile, tools

required_conan_version = ">=1.28.0"

class TaoCPPSequencesonan(ConanFile):
    name = "taocpp-sequences"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/taocpp/sequences"
    description = "Variadic templates and std::integer_sequence support library"
    topics = ("variadic-template", "template", "interger-sequence")
    no_copy_source = True
    settings = "compiler"

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
        extracted_dir = "sequences-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "taocpp-sequences"
        self.cpp_info.filenames["cmake_find_package_multi"] = "taocpp-sequences"
        self.cpp_info.names["cmake_find_package"] = "taocpp"
        self.cpp_info.names["cmake_find_package_multi"] = "taocpp"
        self.cpp_info.components["_taocpp-sequences"].names["cmake_find_package"] = "sequences"
        self.cpp_info.components["_taocpp-sequences"].names["cmake_find_package_multi"] = "sequences"
