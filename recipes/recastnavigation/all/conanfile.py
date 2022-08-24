import os
from conan import ConanFile, tools
from conans import CMake

required_conan_version = ">=1.33.0"


class RecastNavigationConan(ConanFile):
    name = "recastnavigation"
    homepage = "https://github.com/recastnavigation/recastnavigation"
    description = " Navigation-mesh Toolset for Games"
    topics = ("conan", "navmesh", "recast", "navigation", "crowd")
    url = "https://github.com/conan-io/conan-center-index"
    license = "Zlib"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    short_paths = True

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

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["RECASTNAVIGATION_DEMO"] = False
        self._cmake.definitions["RECASTNAVIGATION_TESTS"] = False
        self._cmake.definitions["RECASTNAVIGATION_EXAMPLES"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("License.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "recastnavigation"
        self.cpp_info.names["cmake_find_package_multi"] = "recastnavigation"
        self.cpp_info.components["Recast"].names["cmake_find_package"] = "Recast"
        self.cpp_info.components["Recast"].names["cmake_find_package_multi"] = "Recast"
        self.cpp_info.components["Recast"].libs = ["Recast"]

        self.cpp_info.components["Detour"].names["cmake_find_package"] = "Detour"
        self.cpp_info.components["Detour"].names["cmake_find_package_multi"] = "Detour"
        self.cpp_info.components["Detour"].libs = ["Detour"]

        self.cpp_info.components["DetourCrowd"].names["cmake_find_package"] = "DetourCrowd"
        self.cpp_info.components["DetourCrowd"].names["cmake_find_package_multi"] = "DetourCrowd"
        self.cpp_info.components["DetourCrowd"].libs = ["DetourCrowd"]
        self.cpp_info.components["DetourCrowd"].requires = ["Detour"]

        self.cpp_info.components["DetourTileCache"].names["cmake_find_package"] = "DetourTileCache"
        self.cpp_info.components["DetourTileCache"].names["cmake_find_package_multi"] = "DetourTileCache"
        self.cpp_info.components["DetourTileCache"].libs = ["DetourTileCache"]
        self.cpp_info.components["DetourTileCache"].requires = ["Detour"]

        self.cpp_info.components["DebugUtils"].names["cmake_find_package"] = "DebugUtils"
        self.cpp_info.components["DebugUtils"].names["cmake_find_package_multi"] = "DebugUtils"
        self.cpp_info.components["DebugUtils"].libs = ["DebugUtils"]
        self.cpp_info.components["DebugUtils"].requires = ["Recast", "Detour", "DetourTileCache"]
