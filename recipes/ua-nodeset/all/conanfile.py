from conans import ConanFile, CMake, tools
import os


class UaNodeSetConan(ConanFile):
    name = "UA-Nodeset"
    license = ""
    author = 'OPCFoundation'
    description = "This repository contains UANodeSets and other normative files which are released with a specification"
    url = 'https://github.com/OPCFoundation/UA-Nodeset'
    default_user = "ar"
    default_channel = "thirdparty"
    generators = "cmake", "virtualenv"
    settings = 'os'


    def source(self):
        git = tools.Git()
        git.clone(
            url="https://github.com/OPCFoundation/UA-Nodeset.git",
            branch="v{}".format(self.version))

    def build(self):
        pass
 

    def package(self):
        self.copy("*", dst="ua-nodeset", src="")


    def package_info(self):
        self.env_info.open62541_NODESET_DIR = os.path.join(self.package_folder, "ua-nodeset")
