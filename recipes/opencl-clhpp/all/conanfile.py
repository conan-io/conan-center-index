from conan import ConanFile
from conan.tools.cmake import CMakeDeps, CMakeToolchain, CMake
from conan.tools.files import copy, get, rmdir
from conan.tools.layout import cmake_layout
import os

required_conan_version = ">=1.50.0"


class OpenclHeadersConan(ConanFile):
    name = "opencl-clhpp"
    description = "C++ bindings for the OpenCL API"
    license = "Apache-2.0"
    topics = ("opencl", "header-only", "api-headers")
    homepage = "https://github.com/KhronosGroup/OpenCL-CLHPP"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        CMakeDeps(self).generate()

        tc = CMakeToolchain(self)
        tc.variables.update({
            "BUILD_DOCS": False,
            "BUILD_EXAMPLES": False,
            "BUILD_TESTING": False
        })
        tc.generate()

    def package_id(self):
        self.info.clear()

    def requirements(self):
        self.requires(f"opencl-headers/{self.version}")
        self.requires(f"opencl-icd-loader/{self.version}")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenCLHeadersCpp")
        self.cpp_info.set_property("cmake_target_name", "OpenCL::HeadersCpp")
        self.cpp_info.set_property("pkg_config_name", "OpenCL")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "OpenCLHeadersCpp"
        self.cpp_info.filenames["cmake_find_package_multi"] = "OpenCLHeadersCpp"
        self.cpp_info.names["cmake_find_package"] = "OpenCL"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenCL"
        self.cpp_info.names["pkg_config"] = "OpenCL"
        self.cpp_info.components["_opencl-hlcpp"].names["cmake_find_package"] = "HeadersCpp"
        self.cpp_info.components["_opencl-hlcpp"].names["cmake_find_package_multi"] = "HeadersCpp"
        self.cpp_info.components["_opencl-hlcpp"].set_property("cmake_target_name", "OpenCL::HeadersCpp")
        self.cpp_info.components["_opencl-hlcpp"].set_property("pkg_config_name", "OpenCL")
        self.cpp_info.components["_opencl-hlcpp"].requires += \
            ["opencl-headers::opencl-headers", "opencl-icd-loader::opencl-icd-loader"]
        self.cpp_info.components["_opencl-hlcpp"].bindirs = []
        self.cpp_info.components["_opencl-hlcpp"].libdirs = []
