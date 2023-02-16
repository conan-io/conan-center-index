from conan import ConanFile
from conan.tools.files import get, copy, rmdir
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout

import os

required_conan_version = ">=1.47.0"

class AwsCAuth(ConanFile):
    name = "aws-c-auth"
    description = "C99 library implementation of AWS client-side authentication: standard credentials providers and signing."
    license = "Apache-2.0",
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-c-auth"
    topics = ("aws", "amazon", "cloud", "authentication", "credentials", "providers", "signing")
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
            try:
                del self.options.fPIC
            except Exception:
                pass
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
        self.requires("aws-c-common/0.8.2")
        self.requires("aws-c-cal/0.5.13")
        if Version(self.version) < "0.6.17":
            self.requires("aws-c-io/0.10.20")
            self.requires("aws-c-http/0.6.13")
        else:
            self.requires("aws-c-io/0.13.4")
            self.requires("aws-c-http/0.6.22")
        if Version(self.version) >= "0.6.5":
            self.requires("aws-c-sdkutils/0.1.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

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
        rmdir(self, os.path.join(self.package_folder, "lib", "aws-c-auth"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "aws-c-auth")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-c-auth")

        self.cpp_info.components["aws-c-auth-lib"].names["cmake_find_package"] = "aws-c-auth"
        self.cpp_info.components["aws-c-auth-lib"].names["cmake_find_package_multi"] = "aws-c-auth"
        self.cpp_info.components["aws-c-auth-lib"].set_property("cmake_target_name", "AWS::aws-c-auth")

        self.cpp_info.components["aws-c-auth-lib"].libs = ["aws-c-auth"]
        self.cpp_info.components["aws-c-auth-lib"].requires = [
            "aws-c-common::aws-c-common-lib",
            "aws-c-cal::aws-c-cal-lib",
            "aws-c-io::aws-c-io-lib",
            "aws-c-http::aws-c-http-lib",
        ]
        if Version(self.version) >= "0.6.5":
            self.cpp_info.components["aws-c-auth-lib"].requires.append("aws-c-sdkutils::aws-c-sdkutils-lib")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "aws-c-auth"
        self.cpp_info.filenames["cmake_find_package_multi"] = "aws-c-auth"
        self.cpp_info.names["cmake_find_package"] = "AWS"
        self.cpp_info.names["cmake_find_package_multi"] = "AWS"
