import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get

required_conan_version = ">=1.52.0"


class BoostExtSmlConan(ConanFile):
    name = "boost-ext-sml"
    description = "C++14 State Machine library"
    topics = ("state-machine", "header-only", "metaprogramming", "design-patterns", "sml")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/boost-ext/sml"
    license = "BSL-1.0"

    package_type = "header-library"
    exports_sources = "include/*", "LICENSE*"
    settings = "compiler"

    def validate(self):
        check_min_cppstd(self, "14")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE*", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*include/*.hpp", self.source_folder, self.package_folder)

    def package_id(self):
        self.info.clear()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "sml")
        # TODO: this library is not part of Boost yet, if it will be part change the namespace tp Boost::
        self.cpp_info.set_property("cmake_target_name", "sml::sml")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
