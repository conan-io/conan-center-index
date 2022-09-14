from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class RapiXMLConan(ConanFile):
    name = "rapidxml"
    description = "RapidXml is an attempt to create the fastest XML parser possible."
    license = ["BSL-1.0", "MIT"]
    topics = ("rapidxml", "xml", "parser")
    homepage = "http://rapidxml.sourceforge.net"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def package_id(self):
        self.info.clear()

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "license.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", src=self.source_folder, dst=os.path.join(self.package_folder, "include", "rapidxml"))

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "rapidxml"))
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
