import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.files import copy, get

required_conan_version = ">=2.1"


class TreeGenConan(ConanFile):
    name = "tree-gen"
    license = "Apache-2.0"
    homepage = "https://github.com/QuTech-Delft/tree-gen"
    url = "https://github.com/conan-io/conan-center-index"
    description = "C++ and Python code generator for tree-like structures common in parser and compiler codebases."
    topics = ("code generation", "tree", "parser", "compiler")
    settings = "os", "compiler", "build_type", "arch"
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("m4/1.4.19")
        if self.settings.os == "Windows":
            self.tool_requires("winflexbison/2.5.24")
        else:
            self.tool_requires("flex/2.6.4")
            self.tool_requires("bison/3.8.2")

    def validate_build(self):
        check_min_cppstd(self, 17)

    def validate(self):
        # A recipe that can be used both as an application (tool_requires) and as a library (requires), we do not
        # want the check_min_cppstd to run in the validate method when the recipe is being used as an application.
        if self.context == "host":
            check_min_cppstd(self, 17)

    def requirements(self):
        self.requires("fmt/11.0.2", transitive_headers=True)
        self.requires("range-v3/0.12.0", transitive_headers=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "generate_tree.cmake", src=os.path.join(self.source_folder, "cmake"), dst=os.path.join(self.package_folder, "lib", "cmake"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["tree-gen"]
        self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))
        self.cpp_info.set_property("cmake_build_modules", [os.path.join("lib", "cmake", "generate_tree.cmake")])
