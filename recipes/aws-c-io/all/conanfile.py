from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rmdir
from conan.tools.scm import Version
import os


required_conan_version = ">=2.4"


class AwsCIO(ConanFile):
    name = "aws-c-io"
    description = "IO and TLS for application protocols"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-c-io"
    topics = ("aws", "amazon", "cloud", "io", "tls",)
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
        # These versions come from aws-sdl-cpp prefetch_crt_dependency.sh file,
        # dont bump them independently, check the file and update all the dependencies at once
        if self.version == "0.15.4":
            self.requires("aws-c-common/0.11.0", transitive_headers=True, transitive_libs=True)
            self.requires("aws-c-cal/0.8.3")
            if self.settings.os in ["Linux", "FreeBSD", "Android"]:
                self.requires("s2n/1.5.9")
        if self.version == "0.14.7":
            self.requires("aws-c-common/0.9.15", transitive_headers=True, transitive_libs=True)
            self.requires("aws-c-cal/0.6.14")
            if self.settings.os in ["Linux", "FreeBSD", "Android"]:
                self.requires("s2n/1.4.16")  # 1.4.11 not available, using next available version
        if self.version == "0.10.9":
            self.requires("aws-c-common/0.6.11", transitive_headers=True, transitive_libs=True)
            self.requires("aws-c-cal/0.5.12")
            if self.settings.os in ["Linux", "FreeBSD", "Android"]:
                self.requires("s2n/1.3.15")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        if Version(self.version) < "0.15.4":
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
        rmdir(self, os.path.join(self.package_folder, "lib", "aws-c-io"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "aws-c-io")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-c-io")
        self.cpp_info.libs = ["aws-c-io"]
        if self.options.shared:
            self.cpp_info.defines.append("AWS_IO_USE_IMPORT_EXPORT")
        if self.settings.os == "Macos":
            self.cpp_info.frameworks.append("Security")
            if Version(self.version) >= "0.15.4":
                self.cpp_info.frameworks.append("Network")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["crypt32", "secur32", "shlwapi"]
