from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=2.4"


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

    implements = ["auto_shared_fpic"]
    languages = "C"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.version == "0.9.3":
            self.requires("aws-c-common/0.11.0", transitive_headers=True, transitive_libs=True)
            self.requires("aws-c-compression/0.3.1")
            # Upstream uses this even if it does not explicitly state it in the CMakeLists
            # Maybe expecting the headers to be there transitively?
            self.requires("aws-c-cal/0.8.3")
            self.requires("aws-c-io/0.15.4", transitive_headers=True, transitive_libs=True)
        if self.version == "0.8.1":
            self.requires("aws-c-common/0.9.15", transitive_headers=True, transitive_libs=True)
            self.requires("aws-c-compression/0.2.18")
            self.requires("aws-c-cal/0.6.14")
            self.requires("aws-c-io/0.14.7", transitive_headers=True, transitive_libs=True)
        if self.version == "0.6.7":
            self.requires("aws-c-common/0.6.11", transitive_headers=True, transitive_libs=True)
            self.requires("aws-c-compression/0.2.14")
            self.requires("aws-c-io/0.10.9", transitive_headers=True, transitive_libs=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        if Version(self.version) < "0.9.3":
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
        rmdir(self, os.path.join(self.package_folder, "lib", "aws-c-http"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "aws-c-http")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-c-http")
        self.cpp_info.libs = ["aws-c-http"]
        if self.options.shared:
            self.cpp_info.defines.append("AWS_HTTP_USE_IMPORT_EXPORT")
