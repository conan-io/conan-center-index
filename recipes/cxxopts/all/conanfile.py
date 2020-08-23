import os
from conans import ConanFile, tools


class CxxOptsConan(ConanFile):
    name = "cxxopts"
    homepage = "https://github.com/jarro2783/cxxopts"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Lightweight C++ option parser library, supporting the standard GNU style syntax for options."
    license = "MIT"
    topics = ("conan", "option-parser", "positional-arguments ", "header-only")
    settings = "compiler"
    options = { "unicode": [True, False] }
    default_options = { "unicode": False }
    no_copy_source = True
    _source_subfolder = "source_subfolder"

    def configure(self):
        tools.check_min_cppstd(self, "11")

    def requirements(self):
        if self.options.unicode:
            self.requires("icu/64.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("{}.hpp".format(self.name), dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        if self.options.unicode:
            self.cpp_info.defines = ["CXXOPTS_USE_UNICODE"]
