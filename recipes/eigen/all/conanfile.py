from conans import ConanFile, tools, CMake
import os

required_conan_version = ">=1.43.0"


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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        self.license = "MPL-2.0" if self.options.MPL2_only else ("MPL-2.0", "LGPL-3.0-or-later")

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def package(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTING"] = False
        cmake.definitions["EIGEN_TEST_NOQT"] = True
        cmake.configure(source_folder=self._source_subfolder)
        cmake.install()

        self.copy("COPYING.*", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "share"))

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
