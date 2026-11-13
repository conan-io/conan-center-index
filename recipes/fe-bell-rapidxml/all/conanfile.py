from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=2.0.0"


class RapidXMLFeBellConan(ConanFile):
    name = "fe-bell-rapidxml"
    description = "RapidXml is an attempt to create the fastest XML parser possible, maintained by Fe-Bell."
    license = "MIT"
    topics = ("xml", "parser", "header-only")
    homepage = "https://github.com/Fe-Bell/RapidXML"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "RapidXML"),
             dst=os.path.join(self.package_folder, "include", "rapidxml"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "fe-bell-rapidxml")
        self.cpp_info.set_property("cmake_target_name", "fe-bell-rapidxml::fe-bell-rapidxml")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
