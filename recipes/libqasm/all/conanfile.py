from conan import ConanFile, tools
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.scm import Git

class LibqasmConan(ConanFile):
    name = "libqasm"
    version = "0.5.0"

    # Optional metadata
    license = "Apache-2.0"
    author = "QuTech-Delft"
    url = "https://center.conan.io"
    description = "Library to parse cQASM files"
    topics = ("code generation", "parser", "compiler", "quantum compilation", "quantum simulation")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_python": [True, False],
        "build_tests": [True, False],
        "compat": [True, False],
        "tree_gen_build_tests": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_python": False,
        "build_tests": False,
        "compat": False,
        "tree_gen_build_tests": False
    }

    def build_requirements(self):
        self.tool_requires("m4/1.4.19")
        if self.settings.os == "Windows":
            self.tool_requires("winflexbison/2.5.24")
        else:
            self.tool_requires("flex/2.6.4")
            self.tool_requires("bison/3.8.2")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self)

    def source(self):
        git = Git(self)
        git.clone(url="https://github.com/QuTech-Delft/libqasm.git", target=".")
        git.checkout("2db9916f8e32c5e36d05cb20cafb87133d4dbf16")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["LIBQASM_BUILD_PYTHON"] = self.options.build_python
        tc.variables["LIBQASM_BUILD_TESTS"] = self.options.build_tests
        tc.variables["LIBQASM_COMPAT"] = self.options.compat
        tc.variables["TREE_GEN_BUILD_TESTS"] = self.options.tree_gen_build_tests
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["cqasm"]
