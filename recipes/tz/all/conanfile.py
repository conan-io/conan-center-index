import os

from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.files import get, copy, rmdir
from conan.tools.layout import basic_layout
from conan.tools.microsoft import unix_path

required_conan_version = ">=1.53.0"

class TzConan(ConanFile):
    name = "tz"
    license = "Unlicense"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.iana.org/time-zones"
    description = "The Time Zone Database contains data that represent the history of local time for many representative locations around the globe."
    topics = ("tz", "tzdb", "time", "zone", "date")
    settings = "os", "build_type", "arch", "compiler"

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler

    def build_requirements(self):
        self.tool_requires("mawk/1.3.4-20230404")
        if self.settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        build_cc = unix_path(self, tc.vars().get("CC_FOR_BUILD" if cross_building(self) else "CC", "cc"))
        awk_path = unix_path(self, os.path.join(self.dependencies.direct_build["mawk"].package_folder, "bin", "mawk"))
        tc.make_args.extend([
            f"cc={build_cc}",
            f"AWK={awk_path}",
        ])
        tc.generate()

    def build(self):
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
