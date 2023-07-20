import os

from conan import ConanFile
from conan.tools.files import copy, get, save
from conan.tools.layout import basic_layout

required_conan_version = ">=1.47.0"


class WafConan(ConanFile):
    name = "waf"
    description = "The Waf build system"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://waf.io"
    topics = ("buildsystem", "pre-built")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _license_text(self):
        _, license, _ = open(os.path.join(self.source_folder, "waf"), "rb").read().split(b'"""', 3)
        return license.decode().lstrip()

    def build(self):
        pass

    def package(self):
        binpath = os.path.join(self.package_folder, "bin")
        libpath = os.path.join(self.package_folder, "lib")

        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._license_text)

        copy(self, "waf", src=self.source_folder, dst=binpath)
        copy(self, "waf-light", src=self.source_folder, dst=binpath)
        copy(self, "waflib/*", src=self.source_folder, dst=libpath)

        if self.settings.os == "Windows":
            copy(self, "waf.bat", src=os.path.join(self.source_folder, "utils"), dst=binpath)

        os.chmod(os.path.join(binpath, "waf"), 0o755)
        os.chmod(os.path.join(binpath, "waf-light"), 0o755)

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        binpath = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH env var: {binpath}")
        self.env_info.PATH.append(binpath)

        wafdir = os.path.join(self.package_folder, "lib")
        self.output.info(f"Setting WAFDIR env var: {wafdir}")
        self.env_info.WAFDIR = wafdir
