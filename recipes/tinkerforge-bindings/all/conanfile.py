from conans import ConanFile, tools, CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"

class TinkerforgeBindingsConan(ConanFile):
    name = "tinkerforge-bindings"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.tinkerforge.com/"
    license = "CC0 1.0 Universal"
    description = "API bindings to control Tinkerforge's Bricks and Bricklets"
    topics = "iot", "maker", "bindings"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _cmake = None
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.compiler == "Visual Studio" and self.options.shared and "MT" in self.settings.compiler.runtime:
            raise ConanInvalidConfiguration("Static runtime + shared is failing to link")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=False)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("license.txt", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_target_name", "tinkerforge::bindings")

        self.cpp_info.names["cmake_find_package"] = "tinkerforge"
        self.cpp_info.names["cmake_find_package_multi"] = "tinkerforge"
        self.cpp_info.filenames["cmake_find_package"] = "tinkerforge-bindings"
        self.cpp_info.filenames["cmake_find_package_multi"] = "tinkerforge-bindings"
        self.cpp_info.components["_bindings"].names["cmake_find_package"] = "bindings"
        self.cpp_info.components["_bindings"].names["cmake_find_package_multi"] = "bindings"
        self.cpp_info.components["_bindings"].libs = ["tinkerforge_bindings"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_bindings"].system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["_bindings"].system_libs = ["advapi32", "ws2_32"]
