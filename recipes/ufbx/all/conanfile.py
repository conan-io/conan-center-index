import os

from conan import ConanFile
from conan.tools.files import copy, get, export_conandata_patches
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout

required_conan_version = ">=1.53.0"


class UfbxConan(ConanFile):
    name = "ufbx"
    description = "Single source file FBX file loader."
    topics = ("fbx", "importer")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ufbx/ufbx"
    license = "MIT"
    no_copy_source = True
    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.21 <4]")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "CMakeLists.txt", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["UFBX_BUILD_SHARED"] = self.options.shared
        tc.variables["UFBX_BUILD_TESTS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=self.source_folder)
        cmake.build()

    def package(self):
        copy(self, "LICENSE", dst=self.package_folder, src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ufbx")
        self.cpp_info.set_property("cmake_target_name", "ufbx::ufbx")

        # These are the libs to link against
        self.cpp_info.libs = ["ufbx"]

        # Set these for find_package to work in CMake
        self.cpp_info.names["cmake_find_package"] = "ufbx"
        self.cpp_info.names["cmake_find_package_multi"] = "ufbx"

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
