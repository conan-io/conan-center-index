import os

from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout

class TzdataConan(ConanFile):
    name = "tz"
    license = "Public Domain"
    url = "https://github.com/conan-io/conan-center-index"
    description = "The Time Zone Database contains data that represent the history of local time for many representative locations around the globe."
    topics = ("tz", "tzdb", "time", "zone", "date")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"

    def package_id(self):
        self.info.clear()

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=False)

    def package(self):
        copy(self, "*", dst=os.path.join(self.package_folder, "res"), src=self.source_folder)
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "NOTICE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.resdirs = ['res']
