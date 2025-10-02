from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, cmake_layout, CMakeToolchain
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=2"


class EigenConan(ConanFile):
    name = "eigen"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://eigen.tuxfamily.org"
    description = "Eigen is a C++ template library for linear algebra: matrices, vectors," \
                  " numerical solvers, and related algorithms."
    topics = ("algebra", "linear-algebra", "matrix", "vector", "numerical", "header-only")
    package_type = "header-library"
    license = ("MPL-2.0", "LGPL-3.0-or-later")  # Taking into account the default value of MPL2_only option

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "MPL2_only": [True, False],
    }
    default_options = {
        "MPL2_only": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        self.license = "MPL-2.0"  # MPL-2 only
        if Version(self.version) >= "5.0.0":
            del self.options.MPL2_only
        elif not self.options.MPL2_only:  # < 5.0.0
            self.license = ("MPL-2.0", "LGPL-3.0-or-later")


    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if Version(self.version) >= "3.4.90-":
            check_min_cppstd(self, 14)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_TESTING"] = not self.conf.get("tools.build:skip_test", default=True, check_type=bool)
        if Version(self.version) >= "5.0.0":
            # TODO consider making EIGEN_BUILD_{BLAS,LAPACK} tunable
            tc.cache_variables["EIGEN_BUILD_BLAS"] = False
            tc.cache_variables["EIGEN_BUILD_LAPACK"] = False
            tc.cache_variables["EIGEN_BUILD_DEMOS"] = False
            tc.cache_variables["EIGEN_BUILD_DOC"] = False
            tc.cache_variables["EIGEN_BUILD_PKGCONFIG"] = False
            tc.cache_variables["EIGEN_BUILD_TESTING"] = tc.cache_variables["BUILD_TESTING"]
        else:
            tc.cache_variables["EIGEN_TEST_NOQT"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        copy(self, "COPYING.*", self.source_folder, os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Eigen3")
        self.cpp_info.set_property("cmake_target_name", "Eigen3::Eigen")
        self.cpp_info.set_property("pkg_config_name", "eigen3")
        self.cpp_info.components["eigen3"].bindirs = []
        self.cpp_info.components["eigen3"].libdirs = []
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["eigen3"].system_libs = ["m"]
        if self.options.get_safe("MPL2_only"):
            self.cpp_info.components["eigen3"].defines = ["EIGEN_MPL2_ONLY"]

        self.cpp_info.components["eigen3"].set_property("cmake_target_name", "Eigen3::Eigen")
        self.cpp_info.components["eigen3"].includedirs = [os.path.join("include", "eigen3")]
