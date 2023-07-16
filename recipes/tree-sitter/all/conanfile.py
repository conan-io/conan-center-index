from conan import ConanFile
from conan.tools.cmake import CMake
from conan.tools.layout import basic_layout
import conan.tools.files as tools
import functools
import os

required_conan_version = ">=1.53.0"


class TreeSitterConan(ConanFile):
    name = "tree-sitter"
    description = "Tree-sitter is a parser generator tool and an incremental parsing library. It can build a concrete syntax tree for a source file and efficiently update the syntax tree as the source file is edited."
    topics = ("parser", "incremental", "rust")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://tree-sitter.github.io/tree-sitter"
    license = "MIT"
    
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

    generators = "CMakeToolchain", "CMakeDeps"
    exports_sources = "CMakeLists.txt"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def layout(self):
        basic_layout(self, src_folder="source")

    def source(self):
        tools.get(self, **self.conan_data["sources"][self.version], strip_root=True)


    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        tools.copy(
            self,
            "LICENSE",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "tree-sitter")
        self.cpp_info.builddirs = ["cmake"]
        self.cpp_info.libs = ["tree-sitter"]
