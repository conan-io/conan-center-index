from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
from conan.tools.layout import basic_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.53.0"

class FixedMathConan(ConanFile):
    name = "fixed_math"
    description = "A High-Performance C++17 Library for Fixed-Point 48.16 Arithmetic"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/arturbac/fixed_math/"
    topics = ("mathematics", "fixed-point")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "header_only": [True, False],
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "header_only": False,
        "shared": False,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "10", # fixed_math requires __has_builtin
            "clang": "7",
            "apple-clang": "12",
            "Visual Studio": "16",
            "msvc": "192",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            self.package_type = "static-library"
            del self.options.fPIC

    def configure(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("shared")
        if self.options.header_only:
            self.options.rm_safe("shared")
            self.options.rm_safe("fPIC")
            self.package_type = "header-library"
        elif self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")

    def layout(self):
        if self.options.header_only:
            basic_layout(self, src_folder="src")
        else:
            cmake_layout(self, src_folder="src")

    def package_id(self):
        if self.info.options.header_only:
            self.info.clear()

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def build_requirements(self):
        if not self.options.header_only:
            self.tool_requires("cmake/[>=3.21 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if self.options.header_only:
            return
        tc = CMakeToolchain(self)
        if is_msvc(self):
            tc.variables["CMAKE_CXX_FLAGS"] = "/Zc:__cplusplus"
        tc.generate()
        venv = VirtualBuildEnv(self)
        venv.generate(scope="build")

    def build(self):
        if not self.options.header_only:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def package(self):
        copy(self, "LICENCE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        if not self.options.header_only:
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        else:
            copy(
                self,
                "*.h",
                os.path.join(self.source_folder, "fixed_lib", "include", "fixedmath"),
                os.path.join(self.package_folder, "include", "fixed_math"),
            )
            copy(
                self,
                "*.hpp",
                os.path.join(self.source_folder, "fixed_lib", "include", "fixedmath"),
                os.path.join(self.package_folder, "include", "fixed_math"),
            )

    def package_info(self):
        if self.options.header_only:
            self.cpp_info.bindirs = []
            self.cpp_info.libdirs = []
        else:
            self.cpp_info.libs = ["fixed_math"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.append("m")

        self.cpp_info.set_property("cmake_file_name", "fixed_math")
        self.cpp_info.set_property("cmake_target_name", "fixed_math::fixed_math")

        if is_msvc(self):
            self.cpp_info.cxxflags.append("/Zc:__cplusplus")
