from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class WTLConan(ConanFile):
    name = "wtl"
    license = "MS-PL"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceforge.net/projects/wtl"
    description = "Windows Template Library (WTL) is a C++ library for developing Windows applications and UI components."
    topics = ("atl", "template library", "windows", "template", "ui", "gdi")

    settings = "os"
    no_copy_source = True

    def configure(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("wtl supported only in Windows")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

    def package(self):
        self.copy("*", dst="include", src=os.path.join(self.source_folder, "include"))
        self.copy("MS-PL.TXT", dst="licenses", src=self.source_folder)

    def package_id(self):
        self.info.header_only()
