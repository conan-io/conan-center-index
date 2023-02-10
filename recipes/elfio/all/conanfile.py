from conan import ConanFile
from conan.tools.layout import basic_layout
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
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
            if Version(self.version) < "3.11":
                check_min_cppstd(self, 11)
            else:
                check_min_cppstd(self, 14)

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package_id(self):
        self.info.clear()

    def package(self):
        copy(
            self,
            pattern="COPYING",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        copy(
            self,
            pattern="LICENSE*",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        copy(
            self,
            pattern=os.path.join("elfio", "*.hpp"),
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "include"),
        )
