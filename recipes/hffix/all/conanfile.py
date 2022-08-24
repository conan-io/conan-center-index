from conan import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class HffixConan(ConanFile):
    name = "hffix"
    description = "Financial Information Exchange Protocol C++ Library"
    license = "BSD-2-Clause"
    topics = ("fixprotocol", "financial")
    homepage = "https://github.com/jamesdbrock/hffix"
    url = "https://github.com/conan-io/conan-center-index"

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
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.resdirs = []
