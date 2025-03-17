from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=2.4"


class AwsCEventStream(ConanFile):
    name = "aws-c-event-stream"
    description = "C99 implementation of the vnd.amazon.eventstream content-type"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-c-event-stream"
    topics = ("aws", "eventstream", "content", )
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
        if self.version == "0.5.1":
            self.requires("aws-c-common/0.11.0", transitive_headers=True, transitive_libs=True)
            self.requires("aws-checksums/0.2.3")
            self.requires("aws-c-io/0.15.4")
        if self.version == "0.4.2":
            self.requires("aws-c-common/0.9.15", transitive_headers=True, transitive_libs=True)
            self.requires("aws-checksums/0.1.18")
            self.requires("aws-c-io/0.14.7")
        if self.version == "0.2.7":
            self.requires("aws-c-common/0.6.11", transitive_headers=True, transitive_libs=True)
            self.requires("aws-checksums/0.1.12")
            self.requires("aws-c-io/0.10.9")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_BINARIES"] = False
        tc.variables["BUILD_TESTING"] = False
        if Version(self.version) < "0.5.1":
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
        rmdir(self, os.path.join(self.package_folder, "lib", "aws-c-event-stream"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "aws-c-event-stream")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-c-event-stream")
        self.cpp_info.libs = ["aws-c-event-stream"]
        if self.options.shared:
            self.cpp_info.defines.append("AWS_EVENT_STREAM_USE_IMPORT_EXPORT")
