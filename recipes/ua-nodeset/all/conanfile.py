from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class UaNodeSetConan(ConanFile):
    name = "ua-nodeset"
    license = "UNKNOWN"  # https://github.com/OPCFoundation/UA-Nodeset/issues/79
    description = "UANodeSets and other normative files which are released with a specification"
    homepage = "https://github.com/OPCFoundation/UA-Nodeset"
    url = "https://github.com/conan-io/conan-center-index"
    topics = (
        "OPC UA", "open62541", "iec-62541",
        "industrial automation", "nodeset"
    )
    
    no_copy_source = True


    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format("UA-Nodeset", "PADIM-1.02-2021-07-21"), "source_subfolder")

    def build(self):
        pass
 

    def package(self):
        self.copy("*", dst="res", src="source_subfolder")


    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = ["res"]
        self.user_info.nodeset_dir = os.path.join(self.package_folder, "res")
