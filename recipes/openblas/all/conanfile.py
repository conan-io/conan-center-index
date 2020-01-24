from conans import ConanFile, CMake, tools
import sys
import os


class OpenBLAS(ConanFile):
    name = "openblas"
    version = "0.3.7"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.openblas.net"
    description = "An optimized BLAS library based on GotoBLAS2 1.13 BSD version"
    topics = (
        "openblas",
        "BLAS",
        "lapack"
    )
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_lapack": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_lapack": False
    }
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename('OpenBLAS-{}'.format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        if self.options.build_lapack:
            self.output.warn(
                "Building with lapack support requires a Fortran compiler.")

        cmake.definitions["NOFORTRAN"] = not self.options.build_lapack
        cmake.definitions["BUILD_WITHOUT_LAPACK"] = not self.options.build_lapack

        if self.settings.compiler == "Visual Studio" and not self.options.shared:
            cmake.definitions["MSVC_STATIC_CRT"] = True

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(
            pattern="LICENSE",
            dst="licenses",
            src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.env_info.OpenBLAS_HOME = self.package_folder
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux": 
            self.cpp_info.system_libs = ["pthread"]
            if self.options.build_lapack:
                self.cpp_info.libs.append("gfortran")
        self.cpp_info.names["cmake_find_package"] = "OpenBLAS"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenBLAS"
        self.cpp_info.names['pkg_config'] = "OpenBLAS"
