import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
from conan.tools.files import copy, get
from conan.tools.scm import Version


class LibqasmConan(ConanFile):
    name = "libqasm"

    # Optional metadata
    license = "Apache-2.0"
    homepage = "https://github.com/QuTech-Delft/libqasm"
    url = "https://github.com/conan-io/conan-center-index"
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

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        self.folders.source = "."
        self.folders.build = os.path.join("build", str(self.settings.build_type))
        self.folders.generators = os.path.join(self.folders.build, "generators")

        self.cpp.package.libs = ["cqasm"]
        self.cpp.package.includedirs = ["include"]
        self.cpp.package.libdirs = ["lib"]

        self.cpp.source.includedirs = ["include"]
        self.cpp.build.libdirs = ["."]

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

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

    def validate(self):
        compiler = self.settings.compiler
        version = Version(self.settings.compiler.version)
        if compiler == "apple-clang":
            if version < "14":
                raise ConanInvalidConfiguration("libqasm requires at least apple-clang++ 14")
        elif compiler == "clang":
            if version < "13":
                raise ConanInvalidConfiguration("libqasm requires at least clang++ 13")
        elif compiler == "gcc":
            if version < "10.0":
                raise ConanInvalidConfiguration("libqasm requires at least g++ 10.0")
        elif compiler == "msvc":
            if version < "19.29":
                raise ConanInvalidConfiguration("libqasm requires at least msvc 19.29")
        else:
            raise ConanInvalidConfiguration("Unsupported compiler")
        if compiler.get_safe("cppstd"):
            check_min_cppstd(self, "20")

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["cqasm"]
