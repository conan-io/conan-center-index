from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.47.0"


class QhullConan(ConanFile):
    name = "qhull"
    description = "Qhull computes the convex hull, Delaunay triangulation, " \
                  "Voronoi diagram, halfspace intersection about a point, " \
                  "furthest-site Delaunay triangulation, and furthest-site " \
                  "Voronoi diagram."
    license = "Qhull"
    topics = ("qhull", "geometry", "convex", "triangulation", "intersection")
    homepage = "http://www.qhull.org"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "reentrant": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "reentrant": True,
    }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def package_id(self):
        del self.info.options.reentrant

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "doc"))
        rmdir(self, os.path.join(self.package_folder, "man"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Qhull")
        self.cpp_info.set_property("cmake_target_name", f"Qhull::{self._qhull_cmake_name}")
        self.cpp_info.set_property("pkg_config_name", self._qhull_pkgconfig_name)

        # TODO: back to global scope once cmake_find_package* generators removed
        self.cpp_info.components["libqhull"].libs = [self._qhull_lib_name]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libqhull"].system_libs.append("m")
        if is_msvc(self) and self.options.shared:
            self.cpp_info.components["libqhull"].defines.extend(["qh_dllimport"])

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "Qhull"
        self.cpp_info.names["cmake_find_package_multi"] = "Qhull"
        self.cpp_info.names["pkg_config"] = self._qhull_pkgconfig_name
        self.cpp_info.components["libqhull"].names["cmake_find_package"] = self._qhull_cmake_name
        self.cpp_info.components["libqhull"].names["cmake_find_package_multi"] = self._qhull_cmake_name
        self.cpp_info.components["libqhull"].names["pkg_config"] = self._qhull_pkgconfig_name
        self.cpp_info.components["libqhull"].set_property("cmake_target_name", f"Qhull::{self._qhull_cmake_name}")
        self.cpp_info.components["libqhull"].set_property("pkg_config_name", self._qhull_pkgconfig_name)

    @property
    def _qhull_cmake_name(self):
        name = ""
        if self.options.reentrant:
            name = "qhull_r" if self.options.shared else "qhullstatic_r"
        else:
            name = "libqhull" if self.options.shared else "qhullstatic"
        return name

    @property
    def _qhull_pkgconfig_name(self):
        name = "qhull"
        if not self.options.shared:
            name += "static"
        if self.options.reentrant:
            name += "_r"
        return name

    @property
    def _qhull_lib_name(self):
        name = "qhull"
        if not self.options.shared:
            name += "static"
        if self.settings.build_type == "Debug" or self.options.reentrant:
            name += "_"
            if self.options.reentrant:
                name += "r"
            if self.settings.build_type == "Debug":
                name += "d"
        return name
