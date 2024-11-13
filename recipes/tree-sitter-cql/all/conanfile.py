from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, replace_in_file, copy
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.53.0"


class TreeSitterCQLConan(ConanFile):
    name = "tree-sitter-cql"
    description = "Tree-sitter parser for Cassandra CQL language"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/shotover/tree-sitter-cql"
    topics = ("parser", "grammar", "tree", "CQL", "cassandra")
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

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=(self.export_sources_folder + "/src"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if is_msvc(self):
            del self.options.shared
            self.package_type = "static-library"
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("tree-sitter/0.24.3", transitive_headers=True, transitive_libs=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["TREE_SITTER_CQL_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _patch_sources(self):
        if not self.options.get_safe("shared"):
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

    def package_info(self):
        self.cpp_info.libs = ["tree-sitter-cql"]
        self.cpp_info.set_property("pkg_config_name", "tree-sitter-cql")

