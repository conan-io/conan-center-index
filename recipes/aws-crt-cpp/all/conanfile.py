from conan import ConanFile
from conan.tools.files import get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=2"


class AwsCrtCpp(ConanFile):
    name = "aws-crt-cpp"
    description = "C++ wrapper around the aws-c-* libraries. Provides Cross-Platform Transport Protocols and SSL/TLS implementations for C++."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-crt-cpp"
    topics = ("aws", "amazon", "cloud", "wrapper")
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

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # Bump these in accordance with aws-sdk-cpp
        self.requires("aws-c-common/0.12.5")
        self.requires("aws-c-sdkutils/0.2.4")
        self.requires("aws-c-io/0.23.2", transitive_headers=True)
        self.requires("aws-c-cal/0.9.8")
        self.requires("aws-c-compression/0.3.1")
        self.requires("aws-c-http/0.10.5", transitive_headers=True)
        self.requires("aws-c-auth/0.9.1", transitive_headers=True)
        self.requires("aws-c-mqtt/0.13.3", transitive_headers=True)
        self.requires("aws-checksums/0.2.6")
        self.requires("aws-c-event-stream/0.5.7")
        self.requires("aws-c-s3/0.9.2")

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.cache_variables['AWS_STATIC_MSVC_RUNTIME_LIBRARY'] = self.settings.os == "Windows" and self.settings.get_safe("compiler.runtime") == "static"
        tc.cache_variables["BUILD_DEPS"] = False
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
        rmdir(self, os.path.join(self.package_folder, "lib", "aws-crt-cpp"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "aws-crt-cpp")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-crt-cpp")
        self.cpp_info.libs = ["aws-crt-cpp"]
        if self.options.shared:
            self.cpp_info.defines.append("AWS_CRT_CPP_USE_IMPORT_EXPORT")
