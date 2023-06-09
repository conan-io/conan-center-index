import os

from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.files import get, copy, rmdir, replace_in_file
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

    def build_requirements(self):
        self.tool_requires("mawk/1.3.4-20230404")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

    def _patch_sources(self):
        # INFO: The Makefile enforces /usr/bin/awk, but we want to use tool requirements
        awk_path = os.path.join(self.dependencies.direct_build['mawk'].package_folder, "bin", "mawk").replace("\\", "/")
        replace_in_file(self, os.path.join(self.source_folder, "Makefile"), "AWK=		awk", f"AWK={awk_path}")

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.make(args=["-C", self.source_folder.replace("\\", "/")])

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        autotools = Autotools(self)
        destdir = self.package_folder.replace('\\', '/')
        autotools.install(args=["-C", self.source_folder.replace("\\", "/"), f"DESTDIR={destdir}"])
        rmdir(self, os.path.join(self.package_folder, "usr", "share", "man"))
        # INFO: The library does not have a public API, it's used to build the zic and zdump tools
        rmdir(self, os.path.join(self.package_folder, "usr", "lib"))

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.resdirs = [os.path.join("usr", "share")]
        self.cpp_info.bindirs = [os.path.join("usr", "bin"), os.path.join("usr", "sbin")]
        self.buildenv_info.define("TZDATA", os.path.join(self.package_folder, "usr", "share", "zoneinfo"))
        self.runenv_info.define("TZDATA", os.path.join(self.package_folder, "usr", "share", "zoneinfo"))
