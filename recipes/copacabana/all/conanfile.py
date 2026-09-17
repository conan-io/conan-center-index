import os

from conan import ConanFile
from conan.tools.files import copy, get

required_conan_version = ">=2.1"


class CopacabanaConan(ConanFile):
    name = "copacabana"
    description = "CMake package tools for building, testing, documenting and packaging C++ libraries."
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jfalcou/copacabana"
    topics = ("cmake", "build-system", "header-only")
    package_type = "build-scripts"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def package_id(self):
        self.info.clear()

    def source(self):
        # Upstream tags this v7; conan needs at least two characters in a version.
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*", os.path.join(self.source_folder, "copacabana"),
             os.path.join(self.package_folder, "res", "copacabana"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = []
        # The tree is included by path at configure time, not found by find_package.
        self.conf_info.define("user.copacabana:source",
                              os.path.join(self.package_folder, "res"))
