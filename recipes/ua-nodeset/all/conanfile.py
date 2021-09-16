from conans import ConanFile, CMake, tools
import os


class UaNodeSetConan(ConanFile):
    name = "UA-Nodeset"
    license = "UNKNOWN"  # https://github.com/OPCFoundation/UA-Nodeset/issues/79
    description = "This repository contains UANodeSets and other normative files which are released with a specification"
    homepage = "https://github.com/OPCFoundation/UA-Nodeset"
    url = "https://www.github.com/conan-io/conan-center-index"
    
    no_copy_source = True


    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def build(self):
        pass
 

    def package(self):
        self.copy("*", dst="res")


    def package_info(self):
        self.cpp_info.libdirs = []
        self.user_info.nodeset_path = os.path.join(self.package_folder, "res")
