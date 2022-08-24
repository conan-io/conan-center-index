from conan import ConanFile, tools
from conan.tools.cmake import CMake
from conan.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.43.0"


class DoubleConversionConan(ConanFile):
    name = "double-conversion"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/double-conversion"
    description = "Efficient binary-decimal and decimal-binary conversion routines for IEEE doubles."
    license = "BSD-3-Clause"
    topics = ("double-conversion", "google", "decimal-binary", "conversion")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"

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

    def validate(self):
        if self.settings.compiler == "Visual Studio" and \
           tools.Version(self.settings.compiler.version) < "14":
            raise ConanInvalidConfiguration("Double Convertion could not be built by MSVC <14")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "double-conversion")
        self.cpp_info.set_property("cmake_target_name", "double-conversion::double-conversion")
        self.cpp_info.libs = ["double-conversion"]
