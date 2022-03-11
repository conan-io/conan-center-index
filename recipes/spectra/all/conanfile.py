from conans import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class SpectraConan(ConanFile):
    name = "spectra"
    description = "A header-only C++ library for large scale eigenvalue problems."
    license = "MPL-2.0"
    topics = ("conan", "spectra", "eigenvalue", "header-only")
    homepage = "https://spectralib.org"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("eigen/3.3.9")

    def validate(self):
        if tools.Version(self.version) >= "1.0.0":
            if self.settings.compiler.get_safe("cppstd"):
                tools.check_min_cppstd(self, 11)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "spectra"
        self.cpp_info.filenames["cmake_find_package_multi"] = "spectra"
        self.cpp_info.names["cmake_find_package"] = "Spectra"
        self.cpp_info.names["cmake_find_package_multi"] = "Spectra"
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
