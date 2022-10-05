from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=1.47.0"


class AwsCCompression(ConanFile):
    name = "aws-c-compression"
    description = "C99 implementation of huffman encoding/decoding"
    topics = ("aws", "amazon", "cloud", "compression", "huffman", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-c-compression"
    license = "Apache-2.0",

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("aws-c-common/0.6.19")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "aws-c-compression"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "aws-c-compression")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-c-compression")
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["aws-c-compression-lib"].libs = ["aws-c-compression"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "aws-c-compression"
        self.cpp_info.filenames["cmake_find_package_multi"] = "aws-c-compression"
        self.cpp_info.names["cmake_find_package"] = "AWS"
        self.cpp_info.names["cmake_find_package_multi"] = "AWS"
        self.cpp_info.components["aws-c-compression-lib"].names["cmake_find_package"] = "aws-c-compression"
        self.cpp_info.components["aws-c-compression-lib"].names["cmake_find_package_multi"] = "aws-c-compression"
        self.cpp_info.components["aws-c-compression-lib"].set_property("cmake_target_name", "AWS::aws-c-compression")
        self.cpp_info.components["aws-c-compression-lib"].requires = ["aws-c-common::aws-c-common-lib"]
