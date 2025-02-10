import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, rm, export_conandata_patches, apply_conandata_patches

required_conan_version = ">=2.0.9"


class VilibConan(ConanFile):
    name = "vilib"
    description = "CUDA Visual Library by RPG. GPU-Accelerated Frontend for High-Speed VIO."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/uzh-rpg/vilib"
    topics = ("computer-vision", "visual-odometry", "visual-features", "cuda")

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
        copy(self, "*.cmake", self.recipe_folder, self.export_sources_folder)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("eigen/3.4.0", transitive_headers=True)
        self.requires("opencv/4.9.0", transitive_headers=True, transitive_libs=True)

    def validate(self):
        check_min_cppstd(self, 11)
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Shared builds on Windows are not supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)
        rmdir(self, "assets")
        rmdir(self, "ros")
        rmdir(self, os.path.join("visual_lib", "test"))

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", self.package_folder, recursive=True)
        copy(self, "vilib-cuda-dep.cmake", self.export_sources_folder, os.path.join(self.package_folder, "lib", "cmake", "vilib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "vilib")
        self.cpp_info.set_property("cmake_target_name", "vilib::vilib")

        self.cpp_info.builddirs.append(os.path.join("lib", "cmake", "vilib"))
        self.cpp_info.set_property("cmake_build_modules", [os.path.join("lib", "cmake", "vilib", "vilib-cuda-dep.cmake")])

        self.cpp_info.libs = ["vilib"]
        self.cpp_info.requires = [
            "eigen::eigen",
            "opencv::opencv_core",
            "opencv::opencv_imgproc",
            "opencv::opencv_features2d",
            "opencv::opencv_highgui",
        ]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "dl", "m", "rt"])
