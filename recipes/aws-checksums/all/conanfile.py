from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
import os

required_conan_version = ">=1.47.0"


class AwsChecksums(ConanFile):
    name = "aws-checksums"
    description = (
        "Cross-Platform HW accelerated CRC32c and CRC32 with fallback to efficient "
        "SW implementations. C interface with language bindings for each of our SDKs."
    )
    topics = ("aws", "checksum", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-checksums"
    license = "Apache-2.0",

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
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
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
        self.requires("aws-c-common/0.6.19")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

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

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "aws-checksums"
        self.cpp_info.filenames["cmake_find_package_multi"] = "aws-checksums"
        self.cpp_info.names["cmake_find_package"] = "AWS"
        self.cpp_info.names["cmake_find_package_multi"] = "AWS"
        self.cpp_info.components["aws-checksums-lib"].names["cmake_find_package"] = "aws-checksums"
        self.cpp_info.components["aws-checksums-lib"].names["cmake_find_package_multi"] = "aws-checksums"
        self.cpp_info.components["aws-checksums-lib"].set_property("cmake_target_name", "AWS::aws-checksums")
        self.cpp_info.components["aws-checksums-lib"].requires = ["aws-c-common::aws-c-common-lib"]
