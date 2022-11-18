from conan import ConanFile
from conan.tools.layout import basic_layout
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd
import os


class ElfioConan(ConanFile):
    name = "elfio"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://elfio.sourceforge.net"
    description = "A header-only C++ library that provides a simple interface for reading and generating files in ELF binary format."
    author = "Serge Lamikhov-Center"
    topics = ("conan", "elfio", "elf")
    license = "MIT"
    settings = "compiler"
    no_copy_source = True

    @property
    def configure(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 14)

    def layout(self):
       basic_layout(self, src_folder="source")

    def source(self):
       get(self, **self.conan_data["sources"][self.version], strip_root=True)
       os.rename("elfio-{}".format(self.version), self._source_subfolder)
    
    def source(self):
        get(**self.conan_data["sources"][self.version])
        os.rename("elfio-{}".format(self.version), self._source_subfolder)

    def package_id(self):
        self.info.clear()

    def package(self):
        copy(self, "COPYING", src=self._source_subfolder, dst="licenses")
        copy(self, pattern=os.path.join("elfio", "*.hpp"), src=self._source_subfolder, dst="include")
