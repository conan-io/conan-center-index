import os

from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout, CMakeToolchain
from conan.tools.files import apply_conandata_patches, copy, get, rmdir

required_conan_version = ">=1.50.0"


class EigenConan(ConanFile):
    name = "eigen"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://eigen.tuxfamily.org"
    description = "Eigen is a C++ template library for linear algebra: matrices, vectors," \
                  " numerical solvers, and related algorithms."
    topics = ("eigen", "algebra", "linear-algebra", "vector", "numerical")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "MPL2_only": [True, False],
    }
    default_options = {
        "MPL2_only": False,
    }
    license = ("MPL-2.0", "LGPL-3.0-or-later")  # Taking into account the default value of MPL2_only option

    def configure(self):
        self.license = "MPL-2.0" if self.options.MPL2_only else ("MPL-2.0", "LGPL-3.0-or-later")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, patch["patch_file"], self.recipe_folder, self.export_sources_folder)

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_TESTING"] = not self.conf.get("tools.build:skip_test", default=True, check_type=bool)
        tc.cache_variables["EIGEN_TEST_NOQT"] = True
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        copy(self, "COPYING.*", self.source_folder, os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Eigen3")
        self.cpp_info.set_property("cmake_target_name", "Eigen3::Eigen")
        self.cpp_info.set_property("pkg_config_name", "eigen3")
        # TODO: back to global scope once cmake_find_package* generators removed
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["eigen3"].system_libs = ["m"]
        if self.options.MPL2_only:
            self.cpp_info.components["eigen3"].defines = ["EIGEN_MPL2_ONLY"]

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "Eigen3"
        self.cpp_info.names["cmake_find_package_multi"] = "Eigen3"
        self.cpp_info.names["pkg_config"] = "eigen3"
        self.cpp_info.components["eigen3"].names["cmake_find_package"] = "Eigen"
        self.cpp_info.components["eigen3"].names["cmake_find_package_multi"] = "Eigen"
        self.cpp_info.components["eigen3"].set_property("cmake_target_name", "Eigen3::Eigen")
        self.cpp_info.components["eigen3"].includedirs = [os.path.join("include", "eigen3")]
