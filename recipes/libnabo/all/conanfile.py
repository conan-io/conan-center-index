from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
import os

required_conan_version = ">=1.53.0"


class LibnaboConan(ConanFile):
    name = "libnabo"
    description = "A fast K Nearest Neighbor library for low-dimensional spaces"
    license = "BSD-3-Clause"
    topics = ("nearest-neighbor", "kd-tree")
    homepage = "https://github.com/ethz-asl/libnabo"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openmp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openmp": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("eigen/3.4.0", transitive_headers=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["USE_OPEN_MP"] = self.options.with_openmp
        tc.cache_variables["USE_OPEN_CL"] = False
        tc.cache_variables["SHARED_LIBS"] = self.options.shared
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "copyright", src=os.path.join(self.source_folder, "debian"),
                                dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libnabo")
        self.cpp_info.set_property("cmake_target_name", "libnabo::nabo")
        # TODO: back to global scope in conan v2
        self.cpp_info.components["nabo"].libs = ["nabo"]

        # TODO: to remove in conan v2
        self.cpp_info.components["nabo"].names["cmake_find_package"] = "nabo"
        self.cpp_info.components["nabo"].names["cmake_find_package_multi"] = "nabo"
        self.cpp_info.components["nabo"].set_property("cmake_target_name", "libnabo::nabo")
        self.cpp_info.components["nabo"].requires = ["eigen::eigen"]
