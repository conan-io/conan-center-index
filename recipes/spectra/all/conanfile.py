import os

from conans import ConanFile, CMake, tools

class SpectraConan(ConanFile):
    name = "spectra"
    description = "A header-only C++ library for large scale eigenvalue problems."
    license = "MPL-2.0"
    topics = ("conan", "spectra", "eigenvalue", "header-only")
    homepage = "https://spectralib.org"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("eigen/3.3.7")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Spectra"
        self.cpp_info.names["cmake_find_package_multi"] = "Spectra"
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
