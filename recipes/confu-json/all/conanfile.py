from conans import ConanFile, tools
from conans.tools import check_min_cppstd
from conans.errors import ConanInvalidConfiguration, ConanException
import os
from conans.tools import Version


class ConfuJson(ConanFile):
    name = "confu-json"
    homepage = "https://github.com/werto87/confu_json"
    description = "uses boost::fusion to help with serialization; json <-> user defined type"
    topics = ("json parse", "serialization", "user defined type")
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        tools.check_min_cppstd(self, "20")
        self.options["boost"].header_only = True

    def requirements(self):
        self.requires("boost/1.76.0")
        self.requires("magic_enum/0.7.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("*.h*", dst="include/confu_json",
                  src="source_subfolder/confu_json")
        self.copy("*LICENSE.md", dst="licenses", keep_path=False)

    def package_id(self):
        self.info.header_only()
