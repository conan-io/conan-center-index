from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.32.0"


class PROPOSALConan(ConanFile):
    name = "proposal"
    homepage = "https://github.com/tudo-astroparticlephysics/PROPOSAL"
    license = "GNU Lesser General Public License v3.0"
    url = "https://github.com/conan-io/conan-center-index"
    description = "monte Carlo based lepton and photon propagator"
    topics = ("propagator", "lepton", "photon", "stochastic")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_python": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_python": False,
    }

    generators = "cmake_find_package", "cmake_paths"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("cubicinterpolation/0.1.4")
        self.requires("spdlog/1.8.2")
        if self.options.with_python:
            self.requires("pybind11/2.6.2")

    @property
    def _minimum_compilers_version(self):
        return {"gcc": "7", "clang": "6", "apple-clang": "6"}

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "14")
        if (
            self.settings.os == "Windows"
            or self.settings.compiler == "Visual Studio"
        ):
            raise ConanInvalidConfiguration(
                "PROPOSAL is not supported on Windows and Visual Studio"
            )

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "PROPOSAL-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["BUILD_PYTHON"] = self.options.with_python
        self._cmake.definitions["BUILD_DOCUMENTATION"] = False
        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "PROPOSAL"
        self.cpp_info.names["cmake_find_package_multi"] = "PROPOSAL"
        self.cpp_info.libs = ["PROPOSAL"]
