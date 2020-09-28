
import os
from conans import CMake, tools
from conans.tools import Version
from conans.model.conan_file import ConanFile
from conans.errors import ConanInvalidConfiguration
import glob


class Embree(ConanFile):
    name = "embree3"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "embree", "raytracing", "rendering")
    description = "Intel's collection of high-performance ray tracing kernels."
    generators = "cmake", "cmake_find_package"
    homepage = "https://embree.github.io/"
    _source_folder = "source_subfolder"
    _build_folder = "build_subfolder"
    exports_sources = "CMakeLists.txt"
    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "geometry_curve": [True, False],
        "geometry_grid": [True, False],
        "geometry_instance": [True, False],
        "geometry_quad": [True, False],
        "geometry_subdivision": [True, False],
        "geometry_triangle": [True, False],
        "geometry_user": [True, False],
        "ray_packets": [True, False],
        "ray_masking": [True, False],
        "backface_culling": [True, False],
        "ignore_invalid_rays": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "geometry_curve": True,
        "geometry_grid": True,
        "geometry_instance": True,
        "geometry_quad": True,
        "geometry_subdivision": True,
        "geometry_triangle": True,
        "geometry_user": True,
        "ray_packets": True,
        "ray_masking": False,
        "backface_culling": False,
        "ignore_invalid_rays": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
    
    def configure(self):
        if self.settings.compiler == "apple-clang" and self.settings.compiler.version == "9.1":
            self.options.shared = True

        version = tools.Version(self.settings.compiler.version)
        if self.settings.compiler == "clang" and version < "4":
            raise ConanInvalidConfiguration("Clang < 4 is not supported")
        elif self.settings.compiler == "Visual Studio" and version < "15":
            raise ConanInvalidConfiguration("Visual Studio < 15 is not supported")

        if self._is_linux_clang_libcxx:
            raise ConanInvalidConfiguration("conan recipe for Embree v{0} \
                cannot be built with clang libc++, use libstdc++ instead".format(self.version))

        elif self._is_mac_apple_clang_static:
            raise ConanInvalidConfiguration("Embree cannot be built into static library with apple-clang,\
                try shared library instead")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        target_name = "{0}-{1}".format("embree", self.version)
        os.rename(target_name, self._source_folder)

    def _configure_cmake(self):
        cmake = CMake(self)

        # Configure CMake library build:
        cmake.definitions["EMBREE_STATIC_LIB"] = not self.options.shared
        cmake.definitions["BUILD_TESTING"] = False
        cmake.definitions["EMBREE_TUTORIALS"] = False
        cmake.definitions["EMBREE_GEOMETRY_CURVE"] = self.options.geometry_curve
        cmake.definitions["EMBREE_GEOMETRY_GRID"] = self.options.geometry_grid
        cmake.definitions["EMBREE_GEOMETRY_INSTANCE"] = self.options.geometry_instance
        cmake.definitions["EMBREE_GEOMETRY_QUAD"] = self.options.geometry_quad
        cmake.definitions["EMBREE_GEOMETRY_SUBDIVISION"] = self.options.geometry_subdivision
        cmake.definitions["EMBREE_GEOMETRY_TRIANGLE"] = self.options.geometry_triangle
        cmake.definitions["EMBREE_GEOMETRY_USER"] = self.options.geometry_user
        cmake.definitions["EMBREE_RAY_PACKETS"] = self.options.ray_packets
        cmake.definitions["EMBREE_RAY_MASK"] = self.options.ray_masking
        cmake.definitions["EMBREE_BACKFACE_CULLING"] = self.options.backface_culling
        cmake.definitions["EMBREE_IGNORE_INVALID_RAYS"] = self.options.ignore_invalid_rays
        cmake.definitions["EMBREE_ISPC_SUPPORT"] = False
        cmake.definitions["EMBREE_TASKING_SYSTEM"] = "INTERNAL"

        cmake.configure(build_folder=self._build_folder)
        return cmake

    def build(self):
        os.remove(os.path.join(self._source_folder, "common", "cmake", "FindTBB.cmake"))
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE.txt", src=self._source_folder, dst="licenses")
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'cmake'))
        for command_file in glob.glob(os.path.join(self.package_folder, "*.command")):
            os.remove(command_file)
        for cmake_file in glob.glob(os.path.join(self.package_folder, "*.cmake")):
            os.remove(cmake_file)

        tools.rmdir(os.path.join(self.package_folder, "cmake"))

        if self.options.shared:
            for dll_pattern_to_remove in ["concrt*.dll", "msvcp*.dll", "vcruntime*.dll"]:
                for dll_to_remove in glob.glob(os.path.join(self.package_folder, "bin", dll_pattern_to_remove)):
                    os.remove(dll_to_remove)
        else:
            tools.rmdir(os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libdirs = [
            "lib"
        ]

        self.cpp_info.includedirs = [
            "include"
        ]

        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl", "m", "pthread"]

    @property
    def _is_linux_clang_libcxx(self):
        return (
            self.settings.os == 'Linux' and
            self.settings.compiler == 'clang' and
            self.settings.compiler.libcxx == 'libc++'
        )

    @property
    def _is_mac_apple_clang_static(self):
        return (
            self.settings.os == 'Macos' and
            self.settings.compiler == 'apple-clang' and
            self.options.shared == False
        )    

