from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rm
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=2.1"


class CoalConan(ConanFile):
    name = "coal"
    description = "An extension of the Flexible Collision Library"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/coal-library/coal"
    topics = ("geometry", "collision")
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"with_qhull": [True, False]}
    default_options = {"with_qhull": False}

    short_paths = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("eigen/[>=3.4.0]", transitive_headers=True)
        self.requires("boost/[>=1.82.0 <2]", transitive_headers=True)
        self.requires("assimp/5.4.3")
        self.requires("octomap/1.10.0")
        if self.options.with_qhull:
            self.requires("qhull/8.0.2")

    def validate(self):
        if self.options.with_qhull and (
            self.dependencies["qhull"].options.shared or not self.dependencies["qhull"].options.reentrant
        ):
            raise ConanInvalidConfiguration(
                "coal:with_qhull=True requires qhull/*:shared=False and qhull/*:reentrant=True"
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.22 <5]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_PYTHON_INTERFACE"] = False
        tc.cache_variables["COAL_HAS_QHULL"] = self.options.with_qhull
        tc.generate()

    def _patch_sources(self):
        if not self.dependencies["octomap"].options.shared:
            replace_in_file(
                self,
                os.path.join(self.source_folder, "src", "CMakeLists.txt"),
                "TARGETS octomap",
                "TARGETS octomap-static",
            )
        if self.options.with_qhull:
            # qhull should always be linked statically so use conan target instead
            replace_in_file(
                self,
                os.path.join(self.source_folder, "src", "CMakeLists.txt"),
                "Qhull::qhull_r",
                "Qhull::qhullstatic_r",
            )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rm(self, "*.cmake", self.package_folder, recursive=True)
        rm(self, "*.pc", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_target_aliases", ["coal"])
        self.cpp_info.libs = ["coal"]
