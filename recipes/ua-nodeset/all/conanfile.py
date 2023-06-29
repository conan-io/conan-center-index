import os

from conan import ConanFile
from conan.tools.files import copy, get, load, save

required_conan_version = ">=1.47.0"


class UaNodeSetConan(ConanFile):
    name = "ua-nodeset"
    license = "MIT"
    description = "UANodeSets and other normative files which are released with a specification"
    homepage = "https://github.com/OPCFoundation/UA-Nodeset"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("opc-ua-specifications", "uanodeset", "normative-files", "companion-specification")

    package_type = "build-scripts"
    settings = "os", "arch", "compiler", "build_type"
    short_paths = True

    def layout(self):
        pass

    def package_id(self):
        self.info.clear()

    def build(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _extract_license(self):
        content = load(self, os.path.join(self.build_folder, "AnsiC", "opcua_clientapi.c"))
        license_contents = content[2 : content.find("*/", 1)]
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_contents)

    def package(self):
        self._extract_license()
        copy(self, "*", dst=os.path.join(self.package_folder, "res"), src=self.build_folder)

    def package_info(self):
        self.conf_info.define("user.ua-nodeset:nodeset_dir", os.path.join(self.package_folder, "res"))
        self.cpp_info.resdirs = ["res"]
        self.cpp_info.libdirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.includedirs = []

        # TODO: to remove in conan v2
        self.user_info.nodeset_dir = os.path.join(self.package_folder, "res")
