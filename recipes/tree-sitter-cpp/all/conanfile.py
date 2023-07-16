from conan import ConanFile
from conan.tools.cmake import CMake
from conan.tools.layout import basic_layout
import conan.tools.files as tools
import os

required_conan_version = ">=1.53.0"


class TreeSitterCPPConan(ConanFile):
    name = "tree-sitter-cpp"
    description = "C++ grammar for tree-sitter"
    topics = ("tree-sitter", "parser", "cplusplus")
    url = "https://github.com/tree-sitter/tree-sitter-cpp"
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
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        tools.get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def requirements(self):
        self.requires("tree-sitter/0.20.6", transitive_headers=True, transitive_libs=True)

    def _patch_sources(self):
        if not self.options.shared:
            tools.replace_in_file(
                self,
                os.path.join(self.source_folder, "src", "parser.c"),
                "__declspec(dllexport)", ""
            )

    def build(self):
        self._patch_sources()
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
        self.cpp_info.set_property("cmake_file_name", "tree-sitter-cpp")
        self.cpp_info.builddirs = ["cmake"]
        self.cpp_info.libs = ["tree-sitter-cpp"]
