from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os


required_conan_version = ">=2.0.9"

class ManifoldConan(ConanFile):
    name = "manifold"
    description = "Geometry library for topological robustness"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/elalish/manifold"
    topics = ("geometry", "topological", "mesh")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_parallel_acceleration": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_parallel_acceleration": False,
    }
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # For CrossSection for 2D support
        self.requires("clipper2/1.4.0")
        if self.options.with_parallel_acceleration:
            self.requires("onetbb/2022.0.0")

    def validate(self):
        check_min_cppstd(self, 17)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.18 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["MANIFOLD_DOWNLOADS"] = False
        tc.cache_variables["MANIFOLD_TEST"] = False
        tc.cache_variables["MANIFOLD_CBIND"] = False
        tc.cache_variables["MANIFOLD_PYBIND"] = False
        tc.cache_variables["MANIFOLD_PAR"] = self.options.with_parallel_acceleration
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("clipper2::clipper2", "cmake_target_name", "Clipper2")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["manifold"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
