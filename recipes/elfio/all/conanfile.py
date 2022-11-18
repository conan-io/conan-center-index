from conan import ConanFile
from conan.tools.layout import basic_layout
from conan.tools.files import get, copy, rename
from conan.tools.build import check_min_cppstd
import os


class ElfioConan(ConanFile):
    name = "elfio"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://elfio.sourceforge.net"
    description = "A header-only C++ library that provides a simple interface for reading and generating files in ELF binary format."
    topics = ("elfio", "elf")
    license = "MIT"
    settings = "compiler"
    no_copy_source = True

    def configure(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 14)

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version])
        rename(self, "elfio-{}".format(self.version), "elfio")

    def package_id(self):
        self.info.clear()

    def package(self):
        copy(self, pattern="COPYING", src=os.path.join(self.source_folder, "elfio"), dst=os.path.join(self.package_folder, "licenses"))
        copy(self, pattern="LICENSE*", src=os.path.join(self.source_folder, "elfio"), dst=os.path.join(self.package_folder, "licenses"))
        copy(self, pattern="*.hpp", src=os.path.join(self.source_folder, "elfio"), dst=os.path.join(self.package_folder, "include"))
