import os
from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class DiceTemplateLibrary(ConanFile):
    name = "dice-template-library"
    description = "This template library is a collection of handy template-oriented code that we, the Data Science Group at UPB, found pretty handy."
    homepage = "https://dice-research.org/"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    topics = ("template", "template-library", "compile-time", "switch", "integral-tuple")
    settings = "build_type", "compiler", "os", "arch"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return "20"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "10.2",
            "clang": "12",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._min_cppstd)
        if self.settings.compiler == "apple-clang":
            raise ConanInvalidConfiguration("apple-clang is not supported because a full concept implementation is needed")
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("MSVC is not supported because a full concept implementation is needed")

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(
            str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("{} {} requires C++20. Your compiler is unknown. Assuming it supports C++20.".format(self.name, self.version))
        elif lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration("{} {} requires C++20, which your compiler does not support.".format(self.name, self.version))

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.set_property("cmake_target_name", self.name)
        self.cpp_info.set_property("cmake_target_aliases", ["{0}::{0}".format(self.name)])
        self.cpp_info.names["cmake_find_package"] = self.name
        self.cpp_info.names["cmake_find_package_multi"] = self.name
