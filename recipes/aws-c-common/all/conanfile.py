from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


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

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "0.6.11":
            del self.options.cpu_extensions

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.options.shared and is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Static runtime + shared is not working for more recent releases")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["AWS_ENABLE_LTO"] = False
        if Version(self.version) >= "0.6.0":
            tc.variables["AWS_WARNINGS_ARE_ERRORS"] = False
        if is_msvc(self):
            tc.variables["STATIC_CRT"] = is_msvc_static_runtime(self)
        tc.variables["USE_CPU_EXTENSIONS"] = self.options.get_safe("cpu_extensions", False)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "aws-c-common"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "aws-c-common")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-c-common")

        self.cpp_info.filenames["cmake_find_package"] = "aws-c-common"
        self.cpp_info.filenames["cmake_find_package_multi"] = "aws-c-common"
        self.cpp_info.names["cmake_find_package"] = "AWS"
        self.cpp_info.names["cmake_find_package_multi"] = "AWS"
        self.cpp_info.components["aws-c-common-lib"].set_property("cmake_target_name", "AWS::aws-c-common")
        self.cpp_info.components["aws-c-common-lib"].names["cmake_find_package"] = "aws-c-common"
        self.cpp_info.components["aws-c-common-lib"].names["cmake_find_package_multi"] = "aws-c-common"

        self.cpp_info.components["aws-c-common-lib"].libs = ["aws-c-common"]
        if self.options.shared:
            self.cpp_info.components["aws-c-common-lib"].defines.append("AWS_COMMON_USE_IMPORT_EXPORT")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["aws-c-common-lib"].system_libs = ["dl", "m", "pthread", "rt"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["aws-c-common-lib"].system_libs = ["bcrypt", "ws2_32"]
            if Version(self.version) >= "0.6.13":
                self.cpp_info.components["aws-c-common-lib"].system_libs.append("shlwapi")
        if not self.options.shared:
            if is_apple_os(self):
                self.cpp_info.components["aws-c-common-lib"].frameworks = ["CoreFoundation"]
        self.cpp_info.components["aws-c-common-lib"].builddirs.append(os.path.join("lib", "cmake"))
