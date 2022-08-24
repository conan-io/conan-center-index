from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class UaNodeSetConan(ConanFile):
    name = "ua-nodeset"
    license = "MIT"
    description = "UANodeSets and other normative files which are released with a specification"
    homepage = "https://github.com/OPCFoundation/UA-Nodeset"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("opc-ua-specifications", "uanodeset", "normative-files", "companion-specification")

    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def _extract_license(self):
        content = tools.load(os.path.join(self.source_folder, self._source_subfolder, "AnsiC", "opcua_clientapi.c"))
        license_contents = content[2:content.find("*/", 1)]
        tools.save("LICENSE", license_contents)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build(self):
        pass


    def package(self):
        self._extract_license()
        self.copy("*", dst="res", src=self._source_subfolder)
        self.copy("LICENSE", dst="licenses")


    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = ["res"]
        self.user_info.nodeset_dir = os.path.join(self.package_folder, "res")

