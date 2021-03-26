import os
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.30.0"


class Gm2calcConan(ConanFile):
    name = "gm2calc"
    license = "GPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/GM2Calc/GM2Calc"
    description = "C++ library to calculate the anomalous magnetic moment of the muon in the MSSM"
    topics = ("conan", "high-energy", "physics", "hep", "magnetic moment", "muon", "MSSM")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("boost/1.75.0")
        self.requires("eigen/3.3.9")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("GM2Calc-{}".format(self.version), self._source_subfolder)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "GM2Calc"
        self.cpp_info.names["cmake_find_package_multi"] = "GM2Calc"
        self.cpp_info.names["pkg_config"] = "gm2calc"
        self.cpp_info.libs = ["gm2calc"]
        self.cpp_info.requires = ["boost::headers", "eigen::eigen"]
