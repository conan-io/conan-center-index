import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class MathterConan(ConanFile):
    name = "mathter"
    description = "Powerful 3D math and small-matrix linear algebra library for games and science."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/petiaccja/Mathter"
    topics = ("game-dev", "linear-algebra", "vector-math", "matrix-library", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_xsimd": [True, False] # XSimd is optionally used for hand-rolled vectorization.
    }
    default_options = {
        "with_xsimd": True
    }
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": 10,
            "clang": 6,
            "gcc": 9,
            "Visual Studio": 16,
        }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.name} requires C++{self._min_cppstd}, "
                                            "which your compiler does not support.")

    def requirements(self):
        if self.options.get_safe("with_xsimd"):
            self.requires("xsimd/13.0.0")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.25 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MATHTER_BUILD_TESTS"] = "OFF"
        tc.variables["MATHTER_BUILD_BENCHMARKS"] = "OFF"
        tc.variables["MATHTER_BUILD_EXAMPLES"] = "OFF"
        tc.variables["MATHTER_ENABLE_SIMD"] = "ON" if self.options.get_safe("with_xsimd") else "OFF"
        tc.generate()
        cmake_deps = CMakeDeps(self)
        cmake_deps.generate()
        venv = VirtualBuildEnv(self)
        venv.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENCE.md", self.source_folder, os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        if self.options.get_safe("with_xsimd"):
            self.cpp_info.defines = ["MATHTER_ENABLE_SIMD=1"]
