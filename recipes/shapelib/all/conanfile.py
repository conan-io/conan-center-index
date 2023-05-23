import os

from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout, CMakeToolchain
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir

required_conan_version = ">=1.53.0"


class ShapelibConan(ConanFile):
    name = "shapelib"
    description = "C library for reading and writing ESRI Shapefiles"
    license = "LGPL-2.0-or-later"
    topics = ("osgeo", "shapefile", "esri", "geospatial")
    homepage = "https://github.com/OSGeo/shapelib"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.compiler.rm_safe("cppstd")
        self.settings.compiler.rm_safe("libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.variables["BUILD_TESTING"] = False
        tc.variables["USE_RPATH"] = False
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rm(self, "*.exe", os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "shapelib")
        self.cpp_info.set_property("cmake_target_name", "shapelib::shp")
        self.cpp_info.set_property("pkg_config_name", "shapelib")

        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["shp"].libs = ["shp"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["shp"].system_libs.append("m")

        # TODO: remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "shapelib"
        self.cpp_info.names["cmake_find_package_multi"] = "shapelib"
        self.cpp_info.components["shp"].names["cmake_find_package"] = "shp"
        self.cpp_info.components["shp"].names["cmake_find_package_multi"] = "shp"
