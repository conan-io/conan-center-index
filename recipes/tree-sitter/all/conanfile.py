import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import get, copy, rmdir
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class TreeSitterConan(ConanFile):
    name = "tree-sitter"
    description = "Tree-sitter is a parser generator tool and an incremental parsing library. It can build a concrete syntax tree for a source file and efficiently update the syntax tree as the source file is edited."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://tree-sitter.github.io/tree-sitter"
    topics = ("parser", "incremental", "rust")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
    }

    def export_sources(self):
        if Version(self.version) < "0.24.1":
            copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            if Version(self.version) >= "0.24.1":
                self.package_type = "static-library"

    def configure(self):
        if Version(self.version) >= "0.24.1" and self.settings.os == "Windows":
            self.options.rm_safe("shared")
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) < "0.24.1":
            tc.variables["TREE_SITTER_SRC_DIR"] = self.source_folder.replace("\\", "/")
            tc.variables["TREE_SITTER_VERSION"] = str(self.version)
        else:
            tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.get_safe("shared", False)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        if Version(self.version) < "0.24.1":
            cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        else:
            cmake.configure(build_script_folder=os.path.join(self.source_folder, "lib"))
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
        self.cpp_info.libs = ["tree-sitter"]
