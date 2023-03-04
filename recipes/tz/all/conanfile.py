import os

from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout

required_conan_version = ">=1.53.0"

class TzConan(ConanFile):
    name = "tz"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    description = "The Time Zone Database contains data that represent the history of local time for many representative locations around the globe."
    topics = ("tz", "tzdb", "time", "zone", "date")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False], "data_only": [True, False]}
    default_options = {"fPIC": True, "data_only": False}

    def package_id(self):
        if self.info.options.data_only:
            self.info.clear()

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

    def package(self):
        if not self.options.data_only:
            autotools = Autotools(self)
            autotools.install(args=["-C", self.source_folder])
        tzdata = [
            "africa",
            "antarctica",
            "asia",
            "australasia",
            "backward",
            "backzone",
            "calendars",
            "checklinks.awk",
            "checktab.awk",
            "etcetera",
            "europe",
            "factory",
            "iso3166.tab",
            "leap-seconds.list",
            "leapseconds",
            "leapseconds.awk",
            "NEWS",
            "northamerica",
            "southamerica",
            "version",
            "ziguard.awk",
            "zishrink.awk",
            "zone.tab",
            "zone1970.tab",
        ]
        for data in tzdata:
            copy(self, data, dst=os.path.join(self.package_folder, "res", "tzdata"), src=self.source_folder)
        copy(self, "theory.html", dst=os.path.join(self.package_folder, "res", "docs"), src=self.source_folder)
        copy(self, "tz-*.html", dst=os.path.join(self.package_folder, "res", "docs"), src=self.source_folder)
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.resdirs = ["res"]
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []
        if not self.options.data_only:
            self.cpp_info.resdirs.append(os.path.join("usr", "share"))
            self.cpp_info.libdirs = [os.path.join("usr", "lib")]
            self.cpp_info.bindirs = [
                os.path.join("usr", "bin"),
                os.path.join("usr", "sbin"),
            ]
            self.cpp_info.libs = ["tz"]

        self.buildenv_info.define("TZDATA", os.path.join(self.package_folder, "res", "tzdata"))
        self.runenv_info.define("TZDATA", os.path.join(self.package_folder, "res", "tzdata"))
