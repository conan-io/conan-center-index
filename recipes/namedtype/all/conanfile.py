import glob
import os
from conans import ConanFile, tools


class NamedTypeConan(ConanFile):
    name = "namedtype"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/joboccara/NamedType"
    description = "Implementation of strong types in C++"
    topics = ("strong types", "header-only")
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("NamedType-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 14)

    def package(self):
        if self.version == "20190324":
            self.copy("*.hpp", dst="include/NamedType", src=self._source_subfolder)
        else:
            self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, 'include'))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
