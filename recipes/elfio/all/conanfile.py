import os
from conan import ConanFile, tools


class ElfioConan(ConanFile):
    name = "elfio"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://elfio.sourceforge.net"
    description = "A header-only C++ library that provides a simple interface for reading and generating files in ELF binary format."
    topics = ("conan", "elfio", "elf")
    license = "MIT"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("elfio-{}".format(self.version), self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        self.copy(pattern=os.path.join("elfio", "*.hpp"), src=self._source_subfolder, dst="include")
