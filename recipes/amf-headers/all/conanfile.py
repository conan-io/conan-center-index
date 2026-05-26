from conan import ConanFile
from conan.tools.files import copy, get, download
import os


required_conan_version = ">=2.0"


class AMFHeadersConan(ConanFile):
    name = "amf-headers"
    description = "AMD Advanced Media Framework (AMF) SDK headers"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/GPUOpen-LibrariesAndSDKs/AMF"
    topics = ("amd", "amf", "ffmpeg", "header-only")
    package_type = "header-library"
    no_copy_source = True

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["headers"], strip_root=True)
        download(self, filename="LICENSE", **self.conan_data["sources"][self.version]["license"])

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h",
             src=os.path.join(self.source_folder, "AMF"),
             dst=os.path.join(self.package_folder, "include", "AMF"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "AMF")
        self.cpp_info.set_property("cmake_target_name", "AMF::AMF")
        self.cpp_info.set_property("pkg_config_name", "amf")
