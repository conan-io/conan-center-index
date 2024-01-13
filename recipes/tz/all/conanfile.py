import os

from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.files import get, copy, rmdir, replace_in_file, download
from conan.tools.layout import basic_layout

required_conan_version = ">=1.53.0"

class TzConan(ConanFile):
    name = "tz"
    license = "Unlicense"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.iana.org/time-zones"
    description = "The Time Zone Database contains data that represent the history of local time for many representative locations around the globe."
    topics = ("tz", "tzdb", "time", "zone", "date")
    settings = "os", "build_type", "arch", "compiler"
    options = {"with_binary_db": [True, False]}
    default_options = {"with_binary_db": False}
    package_type = "application" # This is not an application, but application has the correct traits to provide a runtime dependency on data

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler
        if not self.info.options.with_binary_db:
            self.info.clear()

    def build_requirements(self):
        if self.options.with_binary_db:
            self.tool_requires("mawk/1.3.4-20230404")
            if self._settings_build.os == "Windows":
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(
            self,
            url=self.conan_data["sources"][self.version]["url"],
            sha256=self.conan_data["sources"][self.version]["sha256"],
            strip_root=True
        )
        download(
            self,
            url=self.conan_data["sources"][self.version]["windows_zones_url"],
            filename="windowsZones.xml",
            sha256=self.conan_data["sources"][self.version]["windows_zones_sha256"],
        )

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

    def _patch_sources(self):
        # INFO: The Makefile enforces /usr/bin/awk, but we want to use tool requirements
        awk_path = os.path.join(self.dependencies.direct_build['mawk'].package_folder, "bin", "mawk").replace("\\", "/")
        replace_in_file(self, os.path.join(self.source_folder, "Makefile"), "AWK=		awk", f"AWK={awk_path}")

    def build(self):
        if self.options.with_binary_db:
            self._patch_sources()
            autotools = Autotools(self)
            ldlibs = ""
            if self.settings.os == "Macos":
                ldlibs = "-lintl"
            autotools.make(args=["-C", self.source_folder.replace("\\", "/"), f"LDLIBS={ldlibs}"])

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if self.options.with_binary_db:
            autotools = Autotools(self)
            destdir = self.package_folder.replace('\\', '/')
            autotools.install(args=["-C", self.source_folder.replace("\\", "/"), f"DESTDIR={destdir}"])
            rmdir(self, os.path.join(self.package_folder, "usr", "share", "man"))
            # INFO: The library does not have a public API, it's used to build the zic and zdump tools
            rmdir(self, os.path.join(self.package_folder, "usr", "lib"))
        else:
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
                "windowsZones.xml",
            ]
            for data in tzdata:
                copy(self, data, dst=os.path.join(self.package_folder, "res", "tzdata"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.resdirs = ["res"]
        self.buildenv_info.define("TZDATA", os.path.join(self.package_folder, "res", "tzdata"))
        self.runenv_info.define("TZDATA", os.path.join(self.package_folder, "res", "tzdata"))
        if self.options.with_binary_db:
            self.cpp_info.resdirs = [os.path.join("usr", "share")]
            self.cpp_info.bindirs = [os.path.join("usr", "bin"), os.path.join("usr", "sbin")]
            self.buildenv_info.define("TZDATA", os.path.join(self.package_folder, "usr", "share", "zoneinfo"))
            self.runenv_info.define("TZDATA", os.path.join(self.package_folder, "usr", "share", "zoneinfo"))
