import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.files import copy, get
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class TreeGenConan(ConanFile):
    name = "tree-gen"

    # Optional metadata
    license = "Apache-2.0"
    homepage = "https://github.com/QuTech-Delft/tree-gen"
    url = "https://github.com/conan-io/conan-center-index"
    description = "C++ and Python code generator for tree-like structures common in parser and compiler codebases."
    topics = "code generation"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "fPIC": [True, False],
        "asan_enabled": [True, False],
        "build_tests": [True, False]
    }
    default_options = {
        "fPIC": True,
        "asan_enabled": False,
        "build_tests": False
    }

    exports = "version.py", "include/version.hpp"
    exports_sources = "CMakeLists.txt", "cmake/*", "include/*", "src/*", "test/*"

    def build_requirements(self):
        self.tool_requires("m4/1.4.19")
        if self.settings.os == "Windows":
            self.tool_requires("winflexbison/2.5.24")
        else:
            if self.settings.arch != "armv8":
                self.tool_requires("flex/2.6.4")
                self.tool_requires("bison/3.8.2")

    def requirements(self):
        self.requires("fmt/10.1.1")
        self.requires("range-v3/0.12.0")
        if self.options.build_tests:
            self.requires("gtest/1.14.0")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["ASAN_ENABLED"] = self.options.asan_enabled
        tc.variables["TREE_GEN_BUILD_TESTS"] = self.options.build_tests
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def validate(self):
        compiler = self.settings.compiler
        version = Version(self.settings.compiler.version)
        if compiler == "apple-clang":
            if version < "14":
                raise ConanInvalidConfiguration("tree-gen requires at least apple-clang++ 14")
        elif compiler == "clang":
            if version < "13":
                raise ConanInvalidConfiguration("tree-gen requires at least clang++ 13")
        elif compiler == "gcc":
            if version < "10.0":
                raise ConanInvalidConfiguration("tree-gen requires at least g++ 10.0")
        elif compiler == "msvc":
            if version < "19.29":
                raise ConanInvalidConfiguration("tree-gen requires at least msvc 19.29")
        else:
            raise ConanInvalidConfiguration("Unsupported compiler")
        if compiler.get_safe("cppstd"):
            check_min_cppstd(self, "17")

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
