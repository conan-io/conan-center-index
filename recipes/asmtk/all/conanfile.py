from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, apply_conandata_patches, export_conandata_patches
import os

required_conan_version = ">=2.1"

class AsmjitConan(ConanFile):
    name = "asmtk"
    description = "AsmTK provides concepts that are useful mostly in AOT code-generation."
    license = "Zlib"
    topics = ("asmjit", "compiler", "assembler", "jit", "asmtk")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://asmjit.com"
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

    def requirements(self):
        # INFO: asmtk/globals.h: #include <asmjit/core.h>
        # INFO asmtk consumes asmjit directly
        self.requires("asmjit/cci.20240531", transitive_headers=True)

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["ASMTK_EMBED"] = False
        tc.cache_variables["ASMTK_STATIC"] = not self.options.shared
        tc.cache_variables["ASMTK_TEST"] = False
        tc.cache_variables["ASMJIT_EXTERNAL"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "asmtk")
        self.cpp_info.set_property("cmake_target_name", "asmjit::asmtk")

        self.cpp_info.libs = ["asmtk"]
        if not self.options.shared:
            self.cpp_info.defines = ["ASMTK_STATIC"]
