from conan import ConanFile
from conan.tools.cmake import CMake
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.53.0"


class TreeSitterCConan(ConanFile):
    name = "tree-sitter-c"
    description = "C grammar for tree-sitter."
    topics = ("parser", "grammar", "tree", "c", "ide")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tree-sitter/tree-sitter-c"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    package_type = "shared-library"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    generators = "CMakeToolchain", "CMakeDeps"
    exports_sources = "CMakeLists.txt"

    def layout(self):
        basic_layout(self, src_folder="src")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def requirements(self):
        self.requires("tree-sitter/0.20.6", transitive_headers=True, transitive_libs=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
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

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "tree-sitter-c")
        self.cpp_info.builddirs = ["cmake"]
        self.cpp_info.libs = ["tree-sitter-c"]
