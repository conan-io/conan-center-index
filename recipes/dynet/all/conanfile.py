from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class DynetConan(ConanFile):
    name = "dynet"
    description = "DyNet: The Dynamic Neural Network Toolkit"
    topics = ("dynet", "neural-network")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/clab/dynet"
    license = "Apache License 2.0"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False], 
        "fPIC": [True, False],
        "use_mkl": [True, False],
        "backend": ["cuda", "eigen"],
        "python": [True, False],
        "enable_swig": [True, False],
        "enable_boost": [True, False],
        }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_mkl": False,
        "backend": "eigen",
        "python": False,
        "enable_swig": False,
        "enable_boost": True
        }
    generators = "cmake", "cmake_find_package"
    exports_sources = ["CMakeLists.txt", "patches/*"]

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def configure(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.options.use_mkl:
            raise ConanInvalidConfiguration("MKL is not available in ConanCenter")
        if self.options.backend == "cuda":
            raise ConanInvalidConfiguration("Cuda is not available in ConanCenter")
        if self.options.python:
            raise ConanInvalidConfiguration("Python is not available in ConanCenter")
        if self.options.enable_swig:
            raise ConanInvalidConfiguration("SWIG is not available in ConanCenter")

    def requirements(self):
        if self.options.enable_boost:
            self.requires("boost/1.72.0")
        if self.options.backend == "eigen":
            self.requires("eigen/3.3.7")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def _configure_cmake(self):
        if not hasattr(self, '__cmake'):
            cmake = CMake(self)
            cmake.definitions["BACKEND:STRING"] = self.options.backend
            cmake.definitions["PYTHON:BOOL"] = self.options.python
            cmake.definitions["ENABLE_SWIG:BOOL"] = self.options.enable_swig
            cmake.definitions["ENABLE_BOOST:BOOL"] = self.options.enable_boost
            cmake.configure(build_folder=self._build_subfolder)
            setattr(self, '__cmake', cmake)
        return getattr(self, '__cmake')

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        append_has_c99 = self.options.backend == "eigen" and self.settings.compiler == "Visual Studio" and tools.Version(str(self.settings.compiler.version)) == "14"
        with tools.environment_append({"EIGEN_HAS_C99_MATH": "1"}) if append_has_c99 else tools.no_op():
            cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "DyNet"
        self.cpp_info.names["cmake_find_package_multi"] = "DyNet"
        self.cpp_info.libs = ["dynet"]
