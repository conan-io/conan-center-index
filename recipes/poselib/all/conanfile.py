import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class PoselibConan(ConanFile):
    name = "poselib"
    description = "PoseLib: minimal solvers for calibrated camera pose estimation"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/PoseLib/PoseLib"
    topics = ("pose", "camera", "estimation", "solver")

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
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
            "msvc": "192",
            "Visual Studio": "16",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("eigen/3.4.0", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration(
                f"{self.ref} does not export symbols on Windows for a shared library build."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["MARCH_NATIVE"] = False
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        replace_in_file(self, cmakelists, "-march=native -Wall -Werror -fPIC", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "PoseLib")
        self.cpp_info.set_property("cmake_target_name", "PoseLib::PoseLib")

        suffix = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = ["PoseLib" + suffix]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
