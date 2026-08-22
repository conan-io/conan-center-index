from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, replace_in_file, apply_conandata_patches, copy, export_conandata_patches, rmdir

from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class TreeSitterCConan(ConanFile):
    name = "tree-sitter-c"
    description = "C grammar for tree-sitter."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tree-sitter/tree-sitter-c"
    topics = ("parser", "grammar", "tree", "c", "ide")
    settings = "os", "arch", "compiler", "build_type"
    package_type = "library"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def export_sources(self):
        export_conandata_patches(self)
        if Version(self.version) < "0.23.2":
            copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=os.path.join(self.export_sources_folder, "src"))

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) < "0.23.2":
            tc.variables["TREE_SITTER_C_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def requirements(self):
        self.requires("tree-sitter/0.24.3", transitive_headers=True, transitive_libs=True)

    def _patch_sources(self):
        if Version(self.version) < "0.23.2" and not self.options.shared:
            replace_in_file(
                self,
                os.path.join(self.source_folder, "src", "parser.c"),
                "__declspec(dllexport)", ""
            )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["tree-sitter-c"]
