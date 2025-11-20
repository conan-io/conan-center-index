from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rmdir
import os

required_conan_version = ">=2.4"


class AwsCS3(ConanFile):
    name = "aws-c-s3"
    description = "C99 implementation of the S3 client"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-c-s3"
    topics = ("aws", "amazon", "cloud", "s3")
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
        self.requires("aws-c-common/0.12.5", transitive_headers=True, transitive_libs=True)
        self.requires("aws-c-cal/0.9.8")
        self.requires("aws-c-auth/0.9.1", transitive_headers=True)
        self.requires("aws-c-http/0.10.5")
        self.requires("aws-c-io/0.23.2", transitive_headers=True)
        self.requires("aws-checksums/0.2.6")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.cache_variables['AWS_STATIC_MSVC_RUNTIME_LIBRARY'] = self.settings.os == "Windows" and self.settings.get_safe("compiler.runtime") == "static"
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
        rmdir(self, os.path.join(self.package_folder, "lib", "aws-c-s3"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "aws-c-s3")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-c-s3")
        self.cpp_info.libs = ["aws-c-s3"]
        if self.options.shared:
            self.cpp_info.defines.append("AWS_S3_USE_IMPORT_EXPORT")
