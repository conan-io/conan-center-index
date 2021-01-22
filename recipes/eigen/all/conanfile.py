import os
from conans import ConanFile, tools, CMake


class EigenConan(ConanFile):
    name = "eigen"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://eigen.tuxfamily.org"
    description = "Eigen is a C++ template library for linear algebra: matrices, vectors, \
                   numerical solvers, and related algorithms."
    license = ("MPL-2.0", "LGPL-3.0-or-later")
    topics = ("eigen", "algebra", "linear-algebra", "vector", "numerical")
    settings = "os", "compiler", "build_type", "arch"
    options = {"MPL2_only": [True, False]}
    default_options = {"MPL2_only": False}
    exports_sources = ["patches/*"]
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("eigen-{}".format(self.version), self._source_subfolder)
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

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Eigen3"
        self.cpp_info.names["cmake_find_package_multi"] = "Eigen3"
        self.cpp_info.names["pkg_config"] = "eigen3"
        self.cpp_info.components["eigen3"].names["cmake_find_package"] = "Eigen"
        self.cpp_info.components["eigen3"].names["cmake_find_package_multi"] = "Eigen"
        self.cpp_info.components["eigen3"].includedirs = [os.path.join("include", "eigen3")]
        if self.settings.os == "Linux":
            self.cpp_info.components["eigen3"].system_libs = ["m"]
        if self.options.MPL2_only:
            self.cpp_info.components["eigen3"].defines = ["EIGEN_MPL2_ONLY"]
