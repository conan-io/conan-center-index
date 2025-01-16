import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, download
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc

required_conan_version = ">=2.0"


class CargoCConan(ConanFile):
    name = "cargo-c"
    description = "Rust cargo applet to build and install C-ABI compatible dynamic and static libraries"
    license = "MIT"
    homepage = "https://github.com/lu-zero/cargo-c"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("rust", "cargo", "pre-built")
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def configure(self):
        del self.settings.compiler

    def layout(self):
        basic_layout(self, src_folder="src")

    @property
    def _url_info(self):
        info = self.conan_data["sources"][self.version]
        if self.settings.os in ["Linux", "FreeBSD"]:
            return info["Linux"].get(str(self.settings.arch))
        elif self.settings.os == "Macos":
            return info["Macos"]
        elif self.settings.os == "Windows":
            return info["Windows"]["msvc" if is_msvc(self) else "gcc"]
        return None

    def validate(self):
        if not self._url_info:
            raise ConanInvalidConfiguration(f"cargo-c is not available for {self.settings.os} {self.settings.arch}")

    def build(self):
        get(self, **self._url_info)
        download(self, **self.conan_data["sources"][self.version]["License"], filename="LICENSE")

    def package(self):
        copy(self, "LICENSE", self.build_folder, os.path.join(self.package_folder, "licenses"))
        for f in ["cargo-capi", "cargo-cbuild", "cargo-cinstall", "cargo-ctest"]:
            ext = ".exe" if self.settings.os == "Windows" else ""
            copy(self, f + ext, self.build_folder, os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
