from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.files.files import replace_in_file
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=2.0.9"


class QhullConan(ConanFile):
    name = "qhull"
    description = ("Qhull computes the convex hull, Delaunay triangulation, "
                   "Voronoi diagram, halfspace intersection about a point, "
                   "furthest-site Delaunay triangulation, and furthest-site "
                   "Voronoi diagram.")
    license = "Qhull"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.qhull.org"
    topics = ("geometry", "convex", "triangulation", "intersection")
    package_type = "library"
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
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)
        if self.version == "8.1.alpha4":
            # Fix an accidental incorrect version number in CMakeLists.txt
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "8.1-alpha3", "8.1.alpha4")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_STATIC_LIBS"] = not self.options.shared
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["QHULL_ENABLE_TESTING"] = False
        tc.generate()

    def build(self):
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
        self.cpp_info.set_property("pkg_config_name", "_qhull_all")

        reentrant = self.options.reentrant
        component = self.cpp_info.components["libqhull_r" if reentrant else "libqhull"]
        component.set_property("cmake_target_name", f"Qhull::{self._qhull_cmake_name(reentrant)}")
        component.set_property("pkg_config_name", self._qhull_pkgconfig_name(reentrant))
        component.libs = [self._qhull_lib_name(reentrant)]
        if self.settings.os in ["Linux", "FreeBSD"]:
            component.system_libs.append("m")
        if is_msvc(self) and self.options.get_safe("shared"):
            component.defines.append("qh_dllimport")

        if Version(self.version) >= "8.1.alpha4" and reentrant and not self.options.shared:
            suffix = "_d" if self.settings.build_type == "Debug" else ""
            self.cpp_info.components["libqhullcpp"].set_property("cmake_target_name", "Qhull::qhullcpp")
            self.cpp_info.components["libqhullcpp"].set_property("pkg_config_name", "qhullcpp")
            self.cpp_info.components["libqhullcpp"].libs = [f"qhullcpp{suffix}"]
            self.cpp_info.components["libqhullcpp"].requires = ["libqhull_r"]

    def _qhull_cmake_name(self, reentrant):
        if Version(self.version) < "8.1.alpha4" and not reentrant and self.options.shared:
            return "libqhull"
        return self._qhull_pkgconfig_name(reentrant)

    def _qhull_pkgconfig_name(self, reentrant):
        name = "qhull"
        if not self.options.shared:
            name += "static"
        if reentrant:
            name += "_r"
        return name

    def _qhull_lib_name(self, reentrant):
        name = "qhull"
        if not self.options.shared:
            name += "static"
        if self.settings.build_type == "Debug" or reentrant:
            name += "_"
            if reentrant:
                name += "r"
            if self.settings.build_type == "Debug":
                name += "d"
        return name
