from conan import ConanFile
from conan.tools.scm import Version
from conan.tools.files import get, copy, rmdir
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"


class AwsCHttp(ConanFile):
    name = "aws-c-http"
    description = "C99 implementation of the HTTP/1.1 and HTTP/2 specifications"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-c-http"
    topics = ("aws", "amazon", "cloud", "http", "http2", )
    package_type = "library"
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
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("aws-c-common/0.8.2")
        self.requires("aws-c-compression/0.2.15")
        if Version(self.version) < "0.6.22":
            self.requires("aws-c-io/0.10.20")
        else:
            self.requires("aws-c-io/0.13.4")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

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
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "aws-c-http"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "aws-c-http")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-c-http")

        # TODO: back to global scope in conan v2
        self.cpp_info.components["aws-c-http-lib"].libs = ["aws-c-http"]
        if self.options.shared:
            self.cpp_info.components["aws-c-http-lib"].defines.append("AWS_HTTP_USE_IMPORT_EXPORT")

        # TODO: to remove in conan v2
        self.cpp_info.filenames["cmake_find_package"] = "aws-c-http"
        self.cpp_info.filenames["cmake_find_package_multi"] = "aws-c-http"
        self.cpp_info.names["cmake_find_package"] = "AWS"
        self.cpp_info.names["cmake_find_package_multi"] = "AWS"
        self.cpp_info.components["aws-c-http-lib"].set_property("cmake_target_name", "AWS::aws-c-http")
        self.cpp_info.components["aws-c-http-lib"].names["cmake_find_package"] = "aws-c-http"
        self.cpp_info.components["aws-c-http-lib"].names["cmake_find_package_multi"] = "aws-c-http"
        self.cpp_info.components["aws-c-http-lib"].requires = [
            "aws-c-common::aws-c-common",
            "aws-c-compression::aws-c-compression",
            "aws-c-io::aws-c-io",
        ]
