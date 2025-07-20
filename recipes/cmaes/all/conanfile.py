from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.files import (
    export_conandata_patches,
    get,
    rmdir,
    copy,
    apply_conandata_patches,
)
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
import os

required_conan_version = ">=2.0"

class CmaesConan(ConanFile):
    name = "cmaes"
    license = "LGPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/CMA-ES/libcmaes"
    description = "libcmaes is a multithreaded C++11 library with Python bindings for high performance blackbox stochastic optimization using the CMA-ES algorithm for Covariance Matrix Adaptation Evolution Strategy"
    topics = ("cmaes", "minimization")
    package_type = "library"

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

    def validate_build(self):
        if Version(self.version) == "0.10.0":
          if self.settings.compiler == "msvc":
              raise ConanInvalidConfiguration("cmaes does not support MSVC")

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def requirements(self):
        # Transitive header: https://github.com/CMA-ES/libcmaes/blob/v0.10/include/libcmaes/eigenmvn.h#L36
        self.requires("eigen/3.4.0", transitive_headers=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["LIBCMAES_BUILD_EXAMPLES"] = False
        tc.cache_variables["LIBCMAES_BUILD_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["LIBCMAES_USE_OPENMP"] = False
        tc.cache_variables["LIBCMAES_BUILD_PYTHON"] = False
        tc.cache_variables["LIBCMAES_BUILD_TESTS"] = False
        if Version(self.version) == "0.10.0":
          tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"  # CMake 4 support
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        copy(
            self,
            "COPYING",
            self.source_folder,
            os.path.join(self.package_folder, "licenses"),
        )

    def package_info(self):
        self.cpp_info.libs = ["cmaes"]
        self.cpp_info.set_property("cmake_target_name", "libcmaes::cmaes")
        self.cpp_info.set_property("cmake_file_name", "libcmaes")
        self.cpp_info.set_property("pkg_config_name", "libcmaes")
