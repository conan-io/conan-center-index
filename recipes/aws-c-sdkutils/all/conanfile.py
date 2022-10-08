from conan import ConanFile
from conan.tools.files import get, copy, rmdir
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.52.0"

class AwsCSDKUtils(ConanFile):
    name = "aws-c-sdkutils"
    description = "C99 library implementing AWS SDK specific utilities. Includes utilities for ARN parsing, reading AWS profiles, etc..."
    license = "Apache-2.0",
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-c-sdkutils"
    topics = ("aws", "amazon", "cloud", "utility", "ARN")
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

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
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
        rmdir(self, os.path.join(self.package_folder, "lib", "aws-c-sdkutils"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "aws-c-sdkutils")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-c-sdkutils")

        self.cpp_info.filenames["cmake_find_package"] = "aws-c-sdkutils"
        self.cpp_info.filenames["cmake_find_package_multi"] = "aws-c-sdkutils"
        self.cpp_info.names["cmake_find_package"] = "AWS"
        self.cpp_info.names["cmake_find_package_multi"] = "AWS"
        self.cpp_info.components["aws-c-sdkutils-lib"].names["cmake_find_package"] = "aws-c-sdkutils"
        self.cpp_info.components["aws-c-sdkutils-lib"].names["cmake_find_package_multi"] = "aws-c-sdkutils"
        self.cpp_info.components["aws-c-sdkutils-lib"].set_property("cmake_target_name", "AWS::aws-c-sdkutils")

        self.cpp_info.components["aws-c-sdkutils-lib"].libs = ["aws-c-sdkutils"]
        self.cpp_info.components["aws-c-sdkutils-lib"].requires = ["aws-c-common::aws-c-common-lib"]
