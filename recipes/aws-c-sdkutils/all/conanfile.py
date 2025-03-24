from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=2.4"


class AwsCSDKUtils(ConanFile):
    name = "aws-c-sdkutils"
    description = "C99 library implementing AWS SDK specific utilities. Includes utilities for ARN parsing, reading AWS profiles, etc..."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-c-sdkutils"
    topics = ("aws", "amazon", "cloud", "utility", "ARN")
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

    implements = ["auto_shared_fpic"]
    languages = "C"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.version == "0.2.3":
            self.requires("aws-c-common/0.11.0", transitive_headers=True, transitive_libs=True)
        elif self.version == "0.1.15":
            self.requires("aws-c-common/0.9.15", transitive_headers=True, transitive_libs=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) < "0.2.3":
            tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"
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
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "aws-c-sdkutils")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-c-sdkutils")
        self.cpp_info.libs = ["aws-c-sdkutils"]
        if self.options.shared:
            self.cpp_info.defines.append("AWS_SDKUTILS_USE_IMPORT_EXPORT")
