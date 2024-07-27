from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.scm import Version
import os


required_conan_version = ">=1.53.0"


class AsyncppRecipe(ConanFile):
    name = "asyncpp"
    description = "A C++20 coroutine library for asynchronous and parallel programming."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/project/package"
    topics = ("coroutine", "c++20", "async", "parallel", "concurrency")

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

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "13",
            "clang": "17",
            "msvc": "193",
            "Visual Studio": "17",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        # src_folder must use the same source folder name the project
        cmake_layout(self, src_folder="src")

    def validate(self):
        # validate the minimum cpp standard supported. For C++ projects only
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.settings.compiler == "apple-clang":
            # As per https://en.cppreference.com/w/cpp/compiler_support, apple-clang 14.0.0 partially supports C++20 but not jthread
            raise ConanInvalidConfiguration(f"{self.ref} does not support apple-clang compiler, as it lacks jthread support.")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.25 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ASYNCPP_BUILD_TESTS"] = "OFF"
        tc.variables["ASYNCPP_BUILD_BENCHMARKS"] = "OFF"
        tc.generate()
        venv = VirtualBuildEnv(self)
        venv.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["asyncpp"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.bindirs = ["libs"]

        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["pthread"]
