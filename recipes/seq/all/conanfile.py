from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, rm
import os

required_conan_version = ">=2.1"

class PackageConan(ConanFile):
    name = "seq"
    description = "A collection of original C++14 STL-like containers and related tools"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Thermadiag/seq"
    topics = ("formatting", "hashmap", "radix")
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    short_paths = True
    options = {
        "header_only": [True, False],
    }
    default_options = {
        "header_only": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.header_only:
            self.package_type = "header-library"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        if self.info.options.header_only:
            self.info.clear()

    def validate(self):
        check_min_cppstd(self, 14)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["HEADER_ONLY"] = self.options.header_only
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        if not self.options.header_only:
            rm(self, "*.cpp", os.path.join(self.package_folder, "include"), recursive=True)

    def package_info(self):
        if self.options.header_only:
            self.cpp_info.bindirs = []
            self.cpp_info.libdirs = []
        else:
            self.cpp_info.libs = ["seq"]

        self.cpp_info.set_property("cmake_module_file_name", "seq")
        self.cpp_info.set_property("cmake_module_target_name", "seq::seq")
        self.cpp_info.set_property("pkg_config_name", "seq")
