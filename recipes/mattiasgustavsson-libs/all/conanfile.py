from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
import os.path
import glob

class MattiasgustavssonLibsConan(ConanFile):
    name = "mattiasgustavsson-libs"
    description = "Single-file public domain libraries for C/C++"
    homepage = "https://github.com/mattiasgustavsson/libs"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Public Domain"
    topics = ("utilities", "mattiasgustavsson", "libs")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        print(self.conan_data)
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob('libs-*/')[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(pattern="*.h", dst="include", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
