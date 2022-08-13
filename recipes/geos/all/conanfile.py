from conan import ConanFile
from conans import CMake, tools
import functools
import os

required_conan_version = ">=1.43.0"


class GeosConan(ConanFile):
    name = "geos"
    description = "C++11 library for performing operations on two-dimensional vector geometries"
    license = "LGPL-2.1"
    topics = ("geos", "osgeo", "geometry", "topology", "geospatial")
    homepage = "https://trac.osgeo.org/geos"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "inline": [True, False],
        "utils": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "inline": True,
        "utils": True,
    }

    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _has_inline_option(self):
        return tools.Version(self.version) < "3.11.0"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._has_inline_option:
            del self.options.inline

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, {}):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_BENCHMARKS"] = False
        if self._has_inline_option:
            cmake.definitions["DISABLE_GEOS_INLINE"] = not self.options.inline
        cmake.definitions["BUILD_TESTING"] = False
        cmake.definitions["BUILD_DOCUMENTATION"] = False
        cmake.definitions["BUILD_ASTYLE"] = False
        cmake.definitions["BUILD_GEOSOP"] = self.options.utils
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("geos.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "geos")
        # Avoid to create unwanted geos::geos target
        # (geos_c component overrides this global target and it's fine since it depends on all other components)
        self.cpp_info.set_property("cmake_target_name", "GEOS::geos_c")
        self.cpp_info.set_property("pkg_config_name", "geos")

        self.cpp_info.filenames["cmake_find_package"] = "geos"
        self.cpp_info.filenames["cmake_find_package_multi"] = "geos"
        self.cpp_info.names["cmake_find_package"] = "GEOS"
        self.cpp_info.names["cmake_find_package_multi"] = "GEOS"

        # GEOS::geos_cxx_flags
        self.cpp_info.components["geos_cxx_flags"].set_property("cmake_target_name", "GEOS::geos_cxx_flags")
        self.cpp_info.components["geos_cxx_flags"].defines.append("USE_UNSTABLE_GEOS_CPP_API")
        if self.options.get_safe("inline"):
            self.cpp_info.components["geos_cxx_flags"].defines.append("GEOS_INLINE")
        if self.settings.os == "Windows":
            self.cpp_info.components["geos_cxx_flags"].defines.append("TTMATH_NOASM")

        # GEOS::geos
        self.cpp_info.components["geos_cpp"].set_property("cmake_target_name", "GEOS::geos")
        self.cpp_info.components["geos_cpp"].names["cmake_find_package"] = "geos"
        self.cpp_info.components["geos_cpp"].names["cmake_find_package_multi"] = "geos"
        self.cpp_info.components["geos_cpp"].libs = ["geos"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["geos_cpp"].system_libs.append("m")
        if not self.options.shared and tools.stdcpp_library(self):
            self.cpp_info.components["geos_cpp"].system_libs.append(tools.stdcpp_library(self))
        self.cpp_info.components["geos_cpp"].requires = ["geos_cxx_flags"]

        # GEOS::geos_c
        self.cpp_info.components["geos_c"].set_property("cmake_target_name", "GEOS::geos_c")
        self.cpp_info.components["geos_c"].libs = ["geos_c"]
        self.cpp_info.components["geos_c"].requires = ["geos_cpp"]

        if self.options.utils:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
