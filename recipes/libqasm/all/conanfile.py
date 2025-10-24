import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, replace_in_file
from conan.tools.microsoft import is_msvc

required_conan_version = ">=2.1"


class LibqasmConan(ConanFile):
    name = "libqasm"
    license = "Apache-2.0"
    homepage = "https://github.com/QuTech-Delft/libqasm"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Library to parse cQASM files"
    topics = ("code generation", "parser", "compiler", "quantum compilation", "quantum simulation")
    settings = "os", "compiler", "build_type", "arch"
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("fmt/11.0.2", transitive_headers=True)
        self.requires("tree-gen/1.0.8", transitive_headers=True, transitive_libs=True)
        self.requires("range-v3/0.12.0", transitive_headers=True)
        self.requires("antlr4-cppruntime/4.13.1", transitive_headers=True)

    def validate(self):
        check_min_cppstd(self, 20)
        if self.dependencies["antlr4-cppruntime"].options.shared != self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} requires antlr4-cppruntime to be built with the same shared option value.")

    def build_requirements(self):
        self.tool_requires("tree-gen/<host_version>")
        self.tool_requires("zulu-openjdk/21.0.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()
        env = VirtualBuildEnv(self)
        env.generate()

    def _patch_sources(self):
        werror = "/WX" if is_msvc(self) else "-Werror"
        replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"), werror, "")
        replace_in_file(self, os.path.join(self.source_folder, "test", "CMakeLists.txt"), werror, "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        fix_apple_shared_install_name(self)
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["cqasm"]
