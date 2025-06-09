from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=2.4"


class AwsCCommon(ConanFile):
    name = "aws-c-common"
    description = (
        "Core c99 package for AWS SDK for C. Includes cross-platform "
        "primitives, configuration, data structures, and error handling."
    )
    topics = ("aws", "amazon", "cloud", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-c-common"
    license = "Apache-2.0"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "cpu_extensions": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "cpu_extensions": True,
    }

    implements = ["auto_shared_fpic"]
    languages = "C"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["AWS_ENABLE_LTO"] = False
        tc.variables["AWS_WARNINGS_ARE_ERRORS"] = False
        if is_msvc(self):
            tc.variables["STATIC_CRT"] = is_msvc_static_runtime(self)
        if Version(self.version) < "0.11.0":
            tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"
        tc.variables["USE_CPU_EXTENSIONS"] = self.options.get_safe("cpu_extensions", False)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "aws-c-common")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-c-common")
        self.cpp_info.libs = ["aws-c-common"]
        if self.options.shared:
            self.cpp_info.defines.append("AWS_COMMON_USE_IMPORT_EXPORT")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["dl", "m", "pthread", "rt"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["bcrypt", "ws2_32", "kernel32"]
            if Version(self.version) >= "0.6.13":
                self.cpp_info.system_libs.append("shlwapi")
            if Version(self.version) >= "0.9.15":
                self.cpp_info.system_libs.append("psapi")
        if not self.options.shared:
            if is_apple_os(self):
                self.cpp_info.frameworks = ["CoreFoundation"]
        if Version(self.version) >= "0.11.0":
            self.cpp_info.builddirs.append(os.path.join("lib", "cmake", "aws-c-common", "modules"))
        else:
            self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))
