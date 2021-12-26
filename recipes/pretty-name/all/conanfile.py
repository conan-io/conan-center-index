import os
from conans import ConanFile, tools


class PrettyNameConan(ConanFile):
    name = "pretty-name"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Rechip/pretty-name"
    description = "An easy and consistent way how to get type names in C++"
    topics = ("cpp", "typename")
    settings = ["compiler"]
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses",
                  src=self._source_subfolder)
        self.copy(pattern="*", dst="include",
                  src=os.path.join(self._source_subfolder, "include"))

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "14")

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "pretty-name"
        self.cpp_info.names["cmake_find_package_multi"] = "pretty-name"
