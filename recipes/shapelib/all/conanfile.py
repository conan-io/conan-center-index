from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.43.0"


class ShapelibConan(ConanFile):
    name = "shapelib"
    description = "C library for reading and writing ESRI Shapefiles"
    license = "LGPL-2.0-or-later"
    topics = ("shapelib", "osgeo", "shapefile", "esri", "geospatial")
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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "set(BUILD_TEST ON)", "")
        cmake = CMake(self)
        cmake.definitions["USE_RPATH"] = False
        cmake.configure(build_folder=self._build_subfolder)
        cmake.build(target="shp")

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)

        self.copy("shapefil.h", dst="include", src=self._source_subfolder)

        build_lib_dir = os.path.join(self._build_subfolder, "lib")
        build_bin_dir = os.path.join(self._build_subfolder, "bin")
        self.copy(pattern="*.a", dst="lib", src=build_lib_dir, keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=build_lib_dir, keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src=build_lib_dir, keep_path=False, symlinks=True)
        self.copy(pattern="*.so*", dst="lib", src=build_lib_dir, keep_path=False, symlinks=True)
        self.copy(pattern="*.dll", dst="bin", src=build_bin_dir, keep_path=False)

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
