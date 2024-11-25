from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
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
        "cpp": [True, False],
        "reentrant": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "cpp": False,
        "reentrant": True,
    }
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if Version(self.version) >= "8.1-alpha4":
            if not self.options.cpp:
                self.settings.rm_safe("compiler.cppstd")
                self.settings.rm_safe("compiler.libcxx")
        else:
            del self.options.cpp

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        del self.info.options.reentrant
        self.info.options.rm_safe("cpp")

    def validate(self):
        if self.options.get_safe("cpp"):
            if self.options.shared:
                raise ConanInvalidConfiguration("-o cpp=True is only available with -o shared=False")
            if not self.options.reentrant:
                raise ConanInvalidConfiguration("-o cpp=True is only available with -o reentrant=True")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_STATIC_LIBS"] = not self.options.shared
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["QHULL_ENABLE_TESTING"] = False
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
        self.cpp_info.set_property("pkg_config_name", "_qhull_all")

        if self.options.reentrant:
            self.cpp_info.components["libqhull_r"].set_property("cmake_target_name", f"Qhull::{self._qhull_cmake_name(True)}")
            self.cpp_info.components["libqhull_r"].set_property("pkg_config_name", self._qhull_pkgconfig_name(True))
            self.cpp_info.components["libqhull_r"].libs = [self._qhull_lib_name(True)]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["libqhull_r"].system_libs.append("m")
            if is_msvc(self) and self.options.shared:
                self.cpp_info.components["libqhull_r"].defines.append("qh_dllimport")
        else:
            self.cpp_info.components["libqhull"].set_property("cmake_target_name", f"Qhull::{self._qhull_cmake_name(False)}")
            self.cpp_info.components["libqhull"].set_property("pkg_config_name", self._qhull_pkgconfig_name(False))
            self.cpp_info.components["libqhull"].libs = [self._qhull_lib_name(False)]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["libqhull"].system_libs.append("m")
            if is_msvc(self) and self.options.shared:
                self.cpp_info.components["libqhull"].defines.append("qh_dllimport")

        if self.options.get_safe("cpp"):
            suffix = "_d" if self.settings.build_type == "Debug" else ""
            self.cpp_info.components["libqhullcpp"].set_property("cmake_target_name", "Qhull::qhullcpp")
            self.cpp_info.components["libqhullcpp"].set_property("pkg_config_name", "qhullcpp")
            self.cpp_info.components["libqhullcpp"].libs = [f"qhullcpp{suffix}"]
            self.cpp_info.components["libqhullcpp"].requires = ["libqhull_r"]

    def _qhull_cmake_name(self, reentrant):
        if Version(self.version) < "8.1-alpha4" and not reentrant and self.options.shared:
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
