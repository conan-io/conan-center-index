import os
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.33.0"

class DiceTemplateLibrary(ConanFile):
    description = "some description"
    name = "dice-template-library"
    homepage = "https://dice-research.org/"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("some", "topics")
    license = "mit"
    settings = "build_type", "compiler", "os", "arch"
    generators = "cmake", "cmake_find_package", "cmake_paths"
    exports_sources = "include/*", "CMakeLists.txt", "cmake/*"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
       tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="license", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "DiceTemplateLibrary"
        self.cpp_info.names["cmake_find_package_multi"] = "DiceTemplateLibrary"
