from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.errors import ConanInvalidConfiguration
from conan.tools.scm import Version
import os

required_conan_version = ">=2.4"


class CoalConan(ConanFile):
    name = "coal"
    description = "An extension of the Flexible Collision Library"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/coal-library/coal"
    topics = ("geometry", "collision")
    package_type = "shared-library"
    languages = "C++"
    settings = "os", "arch", "compiler", "build_type"
    options = {"with_qhull": [True, False]}
    default_options = {"with_qhull": False}

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("eigen/[>=3.4.0 <4]", transitive_headers=True)
        self.requires("boost/1.88.0", transitive_headers=True)
        self.requires("assimp/5.4.3")
        self.requires("octomap/1.10.0", transitive_headers=True)
        if self.options.with_qhull:
            self.requires("qhull/8.0.2")

    def validate(self):
        check_min_cppstd(self, 14)
        if self.options.with_qhull and self.dependencies["qhull"].options.shared:
            raise ConanInvalidConfiguration("coal:with_qhull=True requires qhull/*:shared=False due qhullcpp library")
        if self.options.with_qhull and not self.dependencies["qhull"].options.reentrant:
            raise ConanInvalidConfiguration("coal:with_qhull=True requires qhull/*:reentrant=True due libqhull_r library")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_PYTHON_INTERFACE"] = False
        tc.cache_variables["COAL_HAS_QHULL"] = self.options.with_qhull
        tc.cache_variables["BUILD_TESTING"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("octomap", "cmake_target_name", "octomap")
        if self.options.with_qhull:
            deps.set_property("qhull", "cmake_target_name", "Qhull::qhull_r")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["coal"]
        self.cpp_info.defines = ["COAL_HAS_OCTOMAP",
                                 "COAL_HAVE_OCTOMAP",
                                f"OCTOMAP_MAJOR_VERSION={Version(self.version).major}",
                                f"OCTOMAP_MINOR_VERSION={Version(self.version).minor}",
                                f"OCTOMAP_PATCH_VERSION={Version(self.version).patch}",]
