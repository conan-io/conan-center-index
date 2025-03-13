import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get

required_conan_version = ">=2.0"


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
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.86.0", transitive_headers=True, transitive_libs=True)
        self.requires("ceres-solver/2.1.0", transitive_headers=True, transitive_libs=True, options={"use_suitesparse": True})
        self.requires("colmap/3.10", transitive_headers=True, transitive_libs=True)
        self.requires("eigen/3.4.0", transitive_headers=True, transitive_libs=True)
        self.requires("openmp/system")
        self.requires("poselib/2.0.3", transitive_headers=True, transitive_libs=True)
        self.requires("suitesparse-cholmod/5.3.0", transitive_headers=True, transitive_libs=True)


    def validate(self):
        check_min_cppstd(self, 17)
        if not self.dependencies["ceres-solver"].options.use_suitesparse:
            raise ConanInvalidConfiguration("'-o ceres-solver/*:use_suitesparse=True' is required")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.28 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

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
