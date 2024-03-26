from conan import ConanFile
from conan.tools.files import copy
from conan.tools.scm import Git
import os

required_conan_version = ">=2.0.0"

class RocketConan(ConanFile):
    name = "rocket"
    description = "Fast single header signal/slots library for C++"
    license = "public domain"
    topics = ("signal-slots", "observer-pattern")
    homepage = "https://github.com/tripleslash/rocket"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "header-library"

    def source(self):
        git = Git(self)
        git.clone(url="https://github.com/tripleslash/rocket.git", target=".")
        git.checkout(**self.conan_data["sources"][self.version])

    def build(self):
        pass

    def package(self):
        copy(self, "rocket.hpp", self.build_folder, os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.libs = ["rocket"]