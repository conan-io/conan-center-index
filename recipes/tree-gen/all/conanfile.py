import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.env import VirtualBuildEnv
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
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "asan_enabled": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "asan_enabled": False
    }

    @property
    def _should_build_test(self):
        return not self.conf.get("tools.build:skip_test", default=True, check_type=bool)

    @property
    def _min_cpp_std(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "gcc": "10",
            "clang": "13",
            "apple-clang": "14",
            "Visual Studio": "16",
            "msvc": "192"
        }

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
        if self._should_build_test:
            self.requires("gtest/1.14.0")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["ASAN_ENABLED"] = self.options.asan_enabled
        tc.variables["TREE_GEN_BUILD_TESTS"] = self._should_build_test
        tc.generate()
        env = VirtualBuildEnv(self)
        env.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def validate(self):
        compiler = str(self.settings.compiler)
        version = Version(self.settings.compiler.version)
        if compiler in self._minimum_compilers_version:
            min_version = self._minimum_compilers_version[compiler]
            if version < min_version:
                raise ConanInvalidConfiguration(f"tree-gen requires at least {compiler} {min_version}")
        else:
            raise ConanInvalidConfiguration("Unsupported compiler")
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cpp_std)

    def package(self):
        copy(self, "LICENSE.md",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.cmake",
             src=os.path.join(self.source_folder, "cmake"),
             dst=os.path.join(self.package_folder, "cmake"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["tree-gen"]
        self.cpp_info.set_property("cmake_build_modules", [os.path.join("cmake", "generate_tree.cmake")])
