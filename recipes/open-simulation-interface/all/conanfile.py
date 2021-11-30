from conans import ConanFile, CMake, tools
import os
import re
import sys
import shutil

required_conan_version = ">=1.33.0"

class OpenSimulationInterfaceConan(ConanFile):
    name = "open-simulation-interface"
    homepage = "https://github.com/OpenSimulationInterface/open-simulation-interface"
    description = 'Generic interface environmental perception of automated driving functions in virtual scenarios'
    topics = ("asam", "adas", "open simulation", "automated driving")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MPL 2.0"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake", "cmake_paths", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def configure(self):
        del self.settings.compiler.cstd
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("protobuf/3.17.1")

    def build_requirements(self):
        self.build_requires("protobuf/3.17.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

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
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        try:
            shutil.rmtree(os.path.join(self.package_folder, "lib", "cmake"))
        except:
            pass

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "open_simulation_interface"
        self.cpp_info.names["cmake_find_package_multi"] = "open_simulation_interface"
        self.cpp_info.components["libopen_simulation_interface"].names["cmake_find_package"] = "open_simulation_interface"
        self.cpp_info.components["libopen_simulation_interface"].names["cmake_find_package_multi"] = "open_simulation_interface"
        self.cpp_info.components["libopen_simulation_interface"].libs = ["open_simulation_interface"]
        self.cpp_info.components["libopen_simulation_interface"].requires = ["protobuf::libprotobuf"]

