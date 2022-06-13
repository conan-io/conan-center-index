import os
from conans import ConanFile, tools

required_conan_version = ">=1.43.0"

class CtmlLibrariesConan(ConanFile):
    name = "ctml"
    description = "A C++ HTML document constructor only depending on the standard library."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tinfoilboy/CTML"
    topics = ("generator", "html", )
    settings = "os", "arch", "compiler", "build_type",
    generators = "cmake",
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE*", "licenses", self._source_subfolder)
        self.copy("ctml.hpp", "include", os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CTML")
        self.cpp_info.set_property("cmake_target_name", "CTML::CTML")

        self.cpp_info.filenames["cmake_find_package"] = "CTML"
        self.cpp_info.filenames["cmake_find_package_multi"] = "CTML"
        self.cpp_info.names["cmake_find_package"] = "CTML"
        self.cpp_info.names["cmake_find_package_multi"] = "CTML"
