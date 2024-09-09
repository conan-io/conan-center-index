import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, download
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.47.0"


class VswhereConan(ConanFile):
    name = "vswhere"
    description = "Locate Visual Studio 2017 and newer installations"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/microsoft/vswhere"
    topics = ("visual-studio", "pre-built")
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        pass

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def validate(self):
        if not is_msvc(self):
            raise ConanInvalidConfiguration("vswhere is only available for MSVC")

    def source(self):
        pass

    def build(self):
        download(self, **self.conan_data["sources"][self.version]["exe"], filename="vswhere.exe")
        download(self, **self.conan_data["sources"][self.version]["license"], filename="LICENSE.txt")

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "vswhere.exe", self.source_folder, os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        # TODO: Legacy, to be removed on Conan 2.0
        bin_folder = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_folder)
