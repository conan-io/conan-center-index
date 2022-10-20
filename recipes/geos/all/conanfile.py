from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
from conans import tools as tools_legacy
import os

required_conan_version = ">=1.50.0"


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

    @property
    def _has_inline_option(self):
        return Version(self.version) < "3.11.0"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._has_inline_option:
            del self.options.inline

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_BENCHMARKS"] = False
        if self._has_inline_option:
            tc.variables["DISABLE_GEOS_INLINE"] = not self.options.inline
        tc.variables["BUILD_TESTING"] = False
        tc.variables["BUILD_DOCUMENTATION"] = False
        tc.variables["BUILD_ASTYLE"] = False
        tc.variables["BUILD_GEOSOP"] = self.options.utils
        tc.generate()

    def build(self):
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
        if not self.options.shared:
            stdcpp_library = tools_legacy.stdcpp_library(self)
            if stdcpp_library:
                self.cpp_info.components["geos_cpp"].system_libs.append(stdcpp_library)
        self.cpp_info.components["geos_cpp"].requires = ["geos_cxx_flags"]

        # GEOS::geos_c
        self.cpp_info.components["geos_c"].set_property("cmake_target_name", "GEOS::geos_c")
        self.cpp_info.components["geos_c"].libs = ["geos_c"]
        self.cpp_info.components["geos_c"].requires = ["geos_cpp"]

        if self.options.utils:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
