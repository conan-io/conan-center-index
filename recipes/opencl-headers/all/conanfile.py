from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class OpenclHeadersConan(ConanFile):
    name = "opencl-headers"
    description = "C language headers for the OpenCL API"
    license = "Apache-2.0"
    topics = ("opencl", "header-only", "api-headers")
    homepage = "https://github.com/KhronosGroup/OpenCL-Headers"
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

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*", src=os.path.join(self.source_folder, "CL"), dst=os.path.join(self.package_folder, "include", "CL"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenCLHeaders")
        self.cpp_info.set_property("cmake_target_name", "OpenCL::Headers")
        self.cpp_info.set_property("pkg_config_name", "OpenCL")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "OpenCLHeaders"
        self.cpp_info.filenames["cmake_find_package_multi"] = "OpenCLHeaders"
        self.cpp_info.names["cmake_find_package"] = "OpenCL"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenCL"
        self.cpp_info.names["pkg_config"] = "OpenCL"
        self.cpp_info.components["_opencl-headers"].names["cmake_find_package"] = "Headers"
        self.cpp_info.components["_opencl-headers"].names["cmake_find_package_multi"] = "Headers"
        self.cpp_info.components["_opencl-headers"].set_property("cmake_target_name", "OpenCL::Headers")
        self.cpp_info.components["_opencl-headers"].set_property("pkg_config_name", "OpenCL")
        self.cpp_info.components["_opencl-headers"].bindirs = []
        self.cpp_info.components["_opencl-headers"].libdirs = []
