import os
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.30.0"


class Gm2calcConan(ConanFile):
    name = "collier"
    license = "GPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://collier.hepforge.org/"
    description = "Fortran library for the numerical evaluation of one-loop scalar and tensor integrals in perturbative relativistic quantum field theory"
    topics = ("conan", "high-energy", "physics", "hep", "one-loop", "integrals")
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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("COLLIER-{}".format(self.version), self._source_subfolder)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["static"] = "OFF" if self.options.shared else "ON"
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.remove_files_by_mask(self.package_folder, "*Config*.cmake")
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "COLLIER"
        self.cpp_info.names["cmake_find_package_multi"] = "COLLIER"
        self.cpp_info.names["pkg_config"] = "collier"
        self.cpp_info.libs = ["collier", "gfortran"]
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("m")
