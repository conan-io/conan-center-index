import os

from conans import ConanFile, CMake, tools

class OctomapConan(ConanFile):
    name = "octomap"
    description = "An Efficient Probabilistic 3D Mapping Framework Based on Octrees."
    license = "BSD-3-Clause"
    topics = ("conan", "octomap", "octree", "3d", "robotics")
    homepage = "https://github.com/OctoMap/octomap"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "openmp": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "openmp": False
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.definitions["OCTOMAP_OMP"] = self.options.openmp
        cmake.configure(build_folder=self._build_subfolder)
        cmake.build(target="octomap" if self.options.shared else "octomap-static")

    def _patch_sources(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "octomap", "CMakeLists.txt"),
                              "SET( BASE_DIR ${CMAKE_SOURCE_DIR} )",
                              "SET( BASE_DIR ${CMAKE_BINARY_DIR} )")
        # Do not force PIC
        tools.replace_in_file(os.path.join(self._source_subfolder, "octomap", "CMakeModules", "CompilerSettings.cmake"),
                              "ADD_DEFINITIONS(-fPIC)", "")

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=os.path.join(self._source_subfolder, "octomap"))
        source_include_dir = os.path.join(self._source_subfolder, "octomap", "include")
        build_lib_dir = os.path.join(self._build_subfolder, "lib")
        build_bin_dir = os.path.join(self._build_subfolder, "bin")
        self.copy(pattern="*.h", dst="include", src=source_include_dir)
        self.copy(pattern="*.hxx", dst="include", src=source_include_dir)
        self.copy(pattern="*.a", dst="lib", src=build_lib_dir, keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=build_lib_dir, keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src=build_lib_dir, keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src=build_lib_dir, keep_path=False, symlinks=True)
        self.copy(pattern="*.dll", dst="bin", src=build_bin_dir, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["octomap", "octomath"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
