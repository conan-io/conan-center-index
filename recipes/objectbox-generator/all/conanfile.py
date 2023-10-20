import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, download, get
from conan.tools.layout import basic_layout

required_conan_version = ">=1.47.0"


class PackageConan(ConanFile):
    name = "objectbox-generator"
    description = "ObjectBox Generator based on FlatBuffers schema files (fbs) for C and C++"
    license = "GPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/objectbox/objectbox-generator"
    topics = ("database", "code-generator", "objectbox", "pre-built")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD", "Windows", "Macos"] or self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration(f"{self.name} doesn't support current environment")

    def build(self):
        get(self, **self.conan_data["sources"][self.version][str(self.info.settings.os)])
        download(self, **self.conan_data["sources"][self.version]["License"], filename="LICENSE.txt")

    def package(self):
        if self.settings.os != "Windows":
            bin_path = os.path.join(self.build_folder, "objectbox-generator")
            os.chmod(bin_path, os.stat(bin_path).st_mode | 0o111)
        copy(self, "objectbox-generator*",
             src=self.build_folder,
             dst=os.path.join(self.package_folder, "bin"),
             keep_path=False)
        copy(self, "LICENSE.txt",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.build_folder)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        # TODO: Legacy, to be removed on Conan 2.0
        binpath = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH env var: {binpath}")
        self.env_info.PATH.append(binpath)
