import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, rmdir, copy, export_conandata_patches, apply_conandata_patches

required_conan_version = ">=2"

class TsidConan(ConanFile):
    name = "tsid"
    package_type = "library"
    license = ("BSD 2-Clause")
    url = "https://github.com/conan-io/conan-center-index"
    description = (
        "TSID is a C++ library for optimization-based inverse-dynamics control based on the rigid "
        "multi-body dynamics library Pinocchio."
        )
    topics = (
        "control", "robotics", "optimization", "humanoids", "pinocchio", "task-space-inverse-dynamics"
        )

    settings = "os", "compiler", "build_type", "arch"
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
        self.requires("eiquadprog/1.2.9", transitive_headers=True)
        self.requires("pinocchio/3.7.0", options={"shared":True}, transitive_headers=True, transitive_libs=True)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.22 <4]")

    def validate(self):
        if self.settings.compiler == "msvc":
            raise ConanInvalidConfiguration("MSVC is not supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        # todo: need eigenpy https://github.com/stack-of-tasks/eigenpy
        tc.cache_variables["BUILD_PYTHON_INTERFACE"] = False
        tc.cache_variables["BUILD_TESTING"] = False
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["tsid"]
