from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, get, rmdir
import os

required_conan_version = ">=1.53.0"


class AwsChecksums(ConanFile):
    name = "aws-checksums"
    description = (
        "Cross-Platform HW accelerated CRC32c and CRC32 with fallback to efficient "
        "SW implementations. C interface with language bindings for each of our SDKs."
    )
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-checksums"
    topics = ("aws", "checksum", )
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

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("aws-c-common/0.8.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "aws-checksums"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "aws-checksums")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-checksums")
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["aws-checksums-lib"].libs = ["aws-checksums"]
        if self.options.shared:
            self.cpp_info.components["aws-checksums-lib"].defines.append("AWS_CHECKSUMS_USE_IMPORT_EXPORT")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "aws-checksums"
        self.cpp_info.filenames["cmake_find_package_multi"] = "aws-checksums"
        self.cpp_info.names["cmake_find_package"] = "AWS"
        self.cpp_info.names["cmake_find_package_multi"] = "AWS"
        self.cpp_info.components["aws-checksums-lib"].names["cmake_find_package"] = "aws-checksums"
        self.cpp_info.components["aws-checksums-lib"].names["cmake_find_package_multi"] = "aws-checksums"
        self.cpp_info.components["aws-checksums-lib"].set_property("cmake_target_name", "AWS::aws-checksums")
        self.cpp_info.components["aws-checksums-lib"].requires = ["aws-c-common::aws-c-common"]
