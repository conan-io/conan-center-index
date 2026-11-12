import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, rmdir, copy, replace_in_file

required_conan_version = ">=2"

class TsidConan(ConanFile):
    name = "tsid"
    package_type = "shared-library"
    license = "BSD-2-Clause"
    homepage = "https://github.com/stack-of-tasks/tsid"
    url = "https://github.com/conan-io/conan-center-index"
    description = (
        "TSID is a C++ library for optimization-based inverse-dynamics control based on the rigid "
        "multi-body dynamics library Pinocchio."
        )
    topics = (
        "control", "robotics", "optimization", "humanoids", "pinocchio", "task-space-inverse-dynamics"
        )

    settings = "os", "compiler", "build_type", "arch"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("eiquadprog/1.2.9")
        self.requires("pinocchio/3.8.0", transitive_libs=True, transitive_headers=True)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.22]")

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        replace_in_file(
            self,
            os.path.join(self.source_folder, "CMakeLists.txt"),
            "add_project_dependency(pinocchio 2.3.1 REQUIRED)",
            "add_project_dependency(pinocchio 3.0.0 REQUIRED)",
        )

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_DOCUMENTATION"] = False # jrl-cmakemodules default: BUILD_DOCUMENTATION=ON,
        tc.cache_variables["BUILD_PYTHON_INTERFACE"] = False
        tc.cache_variables["BUILD_TESTING"] = False
        tc.generate()

    def build(self):
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
