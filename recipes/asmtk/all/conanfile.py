from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, apply_conandata_patches, export_conandata_patches
import os

required_conan_version = ">=1.53.0"

class AsmjitConan(ConanFile):
    name = "asmtk"
    description = "AsmTK is a sister project of AsmJit library, " \
        "which provides concepts that are useful mostly in AOT code-generation."
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

    def requirements(self):
        self.requires("asmjit/cci.20240531", transitive_headers=True, transitive_libs=True)

    def export_sources(self):
        export_conandata_patches(self)

    @property
    def _min_cppstd(self):
        return 11

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ASMTK_EMBED"] = False
        tc.variables["ASMTK_STATIC"] = not self.options.shared
        tc.variables["ASMTK_TEST"] = False
        tc.variables["ASMJIT_EXTERNAL"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()


    def build(self):
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
