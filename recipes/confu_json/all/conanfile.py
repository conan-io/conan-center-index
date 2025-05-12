from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=2.0"


class ConfuJson(ConanFile):
    name = "confu_json"
    homepage = "https://github.com/werto87/confu_json"
    description = "Uses boost::fusion to help with serialization; json <-> user defined type"
    topics = ("json", "serialization", "user-defined-type", "header-only")
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"


    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.85.0")
        self.requires("magic_enum/0.9.6")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 20)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE.md", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h*", os.path.join(self.source_folder, "confu_json"),
                           os.path.join(self.package_folder, "include", "confu_json"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.requires = ["boost::headers", "magic_enum::magic_enum"]
