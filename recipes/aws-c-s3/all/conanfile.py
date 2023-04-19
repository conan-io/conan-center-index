from conan import ConanFile
from conan.tools.files import get, copy, rmdir
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.47.0"

class AwsCS3(ConanFile):
    name = "aws-c-s3"
    description = "C99 implementation of the S3 client"
    license = "Apache-2.0",
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-c-s3"
    topics = ("aws", "amazon", "cloud", "s3")
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
        if Version(self.version) < "0.1.49":
            self.requires("aws-c-io/0.10.20")
            self.requires("aws-c-http/0.6.13")
            self.requires("aws-c-auth/0.6.11")
        else:
            self.requires("aws-c-io/0.13.4")
            self.requires("aws-c-http/0.6.22")
            self.requires("aws-c-auth/0.6.17")
        if Version(self.version) >= "0.1.36":
            self.requires("aws-checksums/0.1.13")

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
        rmdir(self, os.path.join(self.package_folder, "lib", "aws-c-s3"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "aws-c-s3")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-c-s3")
        # TODO: back to root level in conan v2
        self.cpp_info.components["aws-c-s3-lib"].libs = ["aws-c-s3"]
        if self.options.shared:
            self.cpp_info.components["aws-c-s3-lib"].defines.append("AWS_S3_USE_IMPORT_EXPORT")

        # TODO: to remove in conan v2
        self.cpp_info.filenames["cmake_find_package"] = "aws-c-s3"
        self.cpp_info.filenames["cmake_find_package_multi"] = "aws-c-s3"
        self.cpp_info.names["cmake_find_package"] = "AWS"
        self.cpp_info.names["cmake_find_package_multi"] = "AWS"
        self.cpp_info.components["aws-c-s3-lib"].names["cmake_find_package"] = "aws-c-s3"
        self.cpp_info.components["aws-c-s3-lib"].names["cmake_find_package_multi"] = "aws-c-s3"
        self.cpp_info.components["aws-c-s3-lib"].set_property("cmake_target_name", "AWS::aws-c-s3")
        self.cpp_info.components["aws-c-s3-lib"].requires = [
            "aws-c-common::aws-c-common",
            "aws-c-io::aws-c-io",
            "aws-c-http::aws-c-http",
            "aws-c-auth::aws-c-auth",
        ]
        if Version(self.version) >= "0.1.36":
            self.cpp_info.components["aws-c-s3-lib"].requires.append("aws-checksums::aws-checksums")
