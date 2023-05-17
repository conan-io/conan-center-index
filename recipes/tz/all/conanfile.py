import os

from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.files import get, copy, rmdir
from conan.tools.layout import basic_layout

required_conan_version = ">=1.53.0"

class TzConan(ConanFile):
    name = "tz"
    license = "Unlicense"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.iana.org/time-zones"
    description = "The Time Zone Database contains data that represent the history of local time for many representative locations around the globe."
    topics = ("tz", "tzdb", "time", "zone", "date")
    settings = "os", "build_type", "arch"

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.make(args=["-C", self.source_folder])

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        autotools = Autotools(self)
        autotools.install(args=["-C", self.source_folder, f"DESTDIR={self.package_folder}"])
        rmdir(self, os.path.join(self.package_folder, "usr", "share", "man"))
        # INFO: The library does not have a public API, it's used to build the zic and zdump tools
        rmdir(self, os.path.join(self.package_folder, "usr", "lib"))

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = [os.path.join("usr", "share")]
        self.cpp_info.bindirs = [os.path.join("usr", "bin"), os.path.join("usr", "sbin")]
        self.buildenv_info.define("TZDATA", os.path.join(self.package_folder, "usr", "share", "zoneinfo"))
        self.runenv_info.define("TZDATA", os.path.join(self.package_folder, "usr", "share", "zoneinfo"))
