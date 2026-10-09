from conan import ConanFile
from conan.tools.build import check_min_cppstd, stdcpp_library
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, replace_in_file
from conan.tools.scm import Version
import os

required_conan_version = ">=2"


class GeosConan(ConanFile):
    name = "geos"
    description = "GEOS is a C++ library for performing operations on two-dimensional vector geometries."
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libgeos.org/"
    topics = ("osgeo", "geometry", "topology", "geospatial")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "utils": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "utils": True,
    }

    @property
    def _min_cppstd(self):
        return "17" if Version(self.version) >= "3.14.0" else "14"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_BUILD_TYPE"] = str(self.settings.build_type)
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["BUILD_DOCUMENTATION"] = False
        tc.cache_variables["BUILD_ASTYLE"] = False
        tc.cache_variables["BUILD_GEOSOP"] = self.options.utils
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5" # CMake 4 support
        tc.generate()

    def _patch_sources(self):
        # Avoid setting CMAKE_BUILD_TYPE default when multi-config generators are used.
        # https://github.com/libgeos/geos/pull/945
        if Version(self.version) <= "3.12.1":
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            "set(CMAKE_BUILD_TYPE ${DEFAULT_BUILD_TYPE})", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        copy(self, "geos.h", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "geos")
        # Avoid to create unwanted geos::geos target
        # (geos_c component overrides this global target and it's fine since it depends on all other components)
        self.cpp_info.set_property("cmake_target_name", "GEOS::geos_c")
        self.cpp_info.set_property("pkg_config_name", "geos")

        # GEOS::geos_cxx_flags
        self.cpp_info.components["geos_cxx_flags"].set_property("cmake_target_name", "GEOS::geos_cxx_flags")
        self.cpp_info.components["geos_cxx_flags"].defines.append("USE_UNSTABLE_GEOS_CPP_API")
        if self.settings.os == "Windows":
            self.cpp_info.components["geos_cxx_flags"].defines.append("TTMATH_NOASM")

        # GEOS::geos
        self.cpp_info.components["geos_cpp"].set_property("cmake_target_name", "GEOS::geos")
        self.cpp_info.components["geos_cpp"].libs = ["geos"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["geos_cpp"].system_libs.append("m")
        if not self.options.shared:
            libcxx = stdcpp_library(self)
            if libcxx:
                self.cpp_info.components["geos_cpp"].system_libs.append(libcxx)
        self.cpp_info.components["geos_cpp"].requires = ["geos_cxx_flags"]

        # GEOS::geos_c
        self.cpp_info.components["geos_c"].set_property("cmake_target_name", "GEOS::geos_c")
        self.cpp_info.components["geos_c"].libs = ["geos_c"]
        self.cpp_info.components["geos_c"].requires = ["geos_cpp"]
