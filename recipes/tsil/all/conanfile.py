import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.30.0"


class TsilConan(ConanFile):
    name = "tsil"
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.niu.edu/spmartin/TSIL/"
    description = "Two-loop Self-energy Integral Library"
    topics = ("conan", "high-energy", "physics", "hep", "two-loop", "integrals")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "TSIL_SIZE": ["TSIL_SIZE_LONG", "TSIL_SIZE_DOUBLE"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "TSIL_SIZE": "TSIL_SIZE_LONG"
    }
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("TSIL does not support {}".format(self.settings.compiler))
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("tsil-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["TSIL_SIZE"] = self.options.TSIL_SIZE
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "tsil"
        self.cpp_info.libs = ["tsil"]
        self.cpp_info.defines.append(str(self.options.TSIL_SIZE))
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("m")
