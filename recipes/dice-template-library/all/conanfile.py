import os
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.33.0"


class DiceTemplateLibrary(ConanFile):
    name = "dice-template-library"
    description = "This template library is a collection of handy template-oriented code that we, the Data Science Group at UPB, found pretty handy."
    homepage = "https://dice-research.org/"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    topics = ("template", "template library", "compile-time", "switch", "integral tuple")
    settings = "build_type", "compiler", "os", "arch"
    generators = "cmake", "cmake_find_package", "cmake_paths"
    exports_sources = "include/*", "CMakeLists.txt", "cmake/*"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return "20"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._min_cppstd)

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
        self.cpp_info.names["cmake_find_package"] = "dice-template-library"
        self.cpp_info.names["cmake_find_package_multi"] = "dice-template-library"
