import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"

class GlomapConan(ConanFile):
    name = "glomap"
    description = "GLOMAP is a general purpose global structure-from-motion pipeline for image-based reconstruction"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/colmap/glomap"
    topics = ("sfm", "structure-from-motion", "3d-reconstruction", "computer-vision", "colmap")

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
            "gcc": "8",
            "clang": "7",
            "apple-clang": "10",
            "msvc": "191",
            "Visual Studio": "15",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        self.options["ceres-solver"].use_suitesparse = True

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.85.0", transitive_headers=True, transitive_libs=True)
        self.requires("ceres-solver/2.1.0", transitive_headers=True, transitive_libs=True)
        self.requires("colmap/3.10", transitive_headers=True, transitive_libs=True)
        self.requires("eigen/3.4.0", transitive_headers=True, transitive_libs=True)
        self.requires("openmp/system")
        self.requires("poselib/2.0.3", transitive_headers=True, transitive_libs=True)
        self.requires("suitesparse-cholmod/5.2.1", transitive_headers=True, transitive_libs=True)


    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if not self.dependencies["ceres-solver"].options.use_suitesparse:
            raise ConanInvalidConfiguration("'-o ceres-solver/*:use_suitesparse=True' is required")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.28 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FETCH_COLMAP"] = False
        tc.variables["FETCH_POSELIB"] = False
        tc.variables["OPENMP_ENABLED"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

        VirtualBuildEnv(self).generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["glomap"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
