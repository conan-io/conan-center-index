from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.system import package_manager
import os


required_conan_version = ">=1.53.0"


class PclConan(ConanFile):
    name = "pcl"
    description = "Point Cloud Library"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/PointCloudLibrary/pcl"
    topics = ("computer vision", "point cloud", "pointcloud", "3d", "pcd", "ply", "stl", "ifs", "vtk")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openmp": [True, False],
        "with_libusb": [True, False],
        "with_png": [True, False],
        "with_qhull": [True, False],
        "with_vtk": [True, False],
        "with_cuda": [True, False],
        "with_pcap": [True, False],
        "with_opengl": [True, False],
        "with_tools": [True, False],
        "with_apps": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openmp": False,
        "with_libusb": False,
        "with_png": True,
        "with_qhull": True,
        "with_vtk": False,
        "with_cuda": False,
        "with_pcap": False,
        "with_opengl": False,
        "with_tools": False,
        "with_apps": False,
    }

    short_paths = True

    @property
    def _min_cppstd(self):
        return 17

    # in case the project requires C++14/17/20/... the minimum compiler version should be listed
    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def system_requirements(self):
        if self.options.with_vtk:
            package_manager.Apt(self).install(["libvtk-dev"])
            package_manager.Dnf(self).install(["vtk-devel"])
            if self.settings.os == "Windows":
                self.output.warn("On Windows VTK must be installed manually.")

    def requirements(self):
        self.requires("zlib/1.2.13")
        # Transitive headers on boost because pcl/point_struct_traits.h:40:10: references boost/mpl/assert.hpp
        self.requires("boost/1.82.0", transitive_headers=True)
        self.requires("eigen/3.4.0", transitive_headers=True)
        self.requires("flann/1.9.2")
        if self.options.with_png:
            self.requires("libpng/1.6.40")
        if self.options.with_qhull:
            self.requires("qhull/8.0.1")
        if self.options.with_apps:
            self.requires("qt/6.5.1")
        if self.options.with_libusb:
            self.requires("libusb/1.0.26")
        if self.options.with_pcap:
            self.requires("libpcap/1.10.4")
        if self.options.with_opengl:
            self.requires("opengl/system")

    def validate(self):
        # validate the minimum cpp standard supported. For C++ projects only
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 191)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PCL_SHARED_LIBS"] = self.options.shared
        tc.variables["WITH_OPENMP"] = self.options.with_openmp
        tc.variables["WITH_LIBUSB"] = self.options.with_libusb
        tc.variables["WITH_PNG"] = self.options.with_png
        tc.variables["WITH_QHULL"] = self.options.with_qhull
        tc.variables["WITH_VTK"] = self.options.with_vtk
        tc.variables["WITH_CUDA"] = self.options.with_cuda
        tc.variables["WITH_PCAP"] = self.options.with_pcap
        tc.variables["WITH_OPENGL"] = self.options.with_opengl
        tc.variables["BUILD_tools"] = self.options.with_tools
        tc.variables["BUILD_apps"] = self.options.with_apps
        tc.variables["BUILD_examples"] = True
        tc.cache_variables["WITH_QT"] = self.options.with_apps
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(variables={"PCL_ONLY_CORE_POINT_TYPES": "ON"})
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        # For the legal reasons, and in order to reduce the size of packages, it's not allowed to package Microsoft Visual Studio runtime libraries, such as msvcr80.dll, msvcp80.dll, vcruntime140.dll and so on.
        # See https://github.com/conan-io/conan-center-index/blob/master/docs/error_knowledge_base.md#kb-h021-ms-runtime-files
        rmdir(self, os.path.join(self.package_folder, "bin"))

    @property
    def _pcl_lib_components(self):
        def usb():
            return ["libusb::libusb"] if self.options.with_libusb else []
        def png():
            return ["libpng::libpng"] if self.options.with_png else []
        def qhull():
            return ["qhull::qhull"] if self.options.with_qhull else []

        return {
            "common": {"requires": ["eigen::eigen3", "boost::boost"]},
            "kdtree": {"requires": ["common", "flann::flann"]},
            "octree": {"requires": ["common"]},
            "search": {"requires": ["common", "kdtree", "octree", "flann::flann"]},
            "sample_consensus": {"requires": ["common", "search"]},
            "filters": {"requires": ["common", "sample_consensus", "search", "kdtree", "octree"]},
            "2d": {"requires": ["common", "filters"], "header_only": True},
            "geometry": {"requires": ["common"], "header_only": True},
            "io": {"requires": ["common", "octree", "zlib::zlib"] + png() + usb(), "extra_libs": ["io_ply"]},
            "features": {"requires": ["common", "search", "kdtree", "octree", "filters", "2d"]},
            "ml": {"requires": ["common"]},
            "segmentation": {"requires": ["common", "geometry", "search", "sample_consensus", "kdtree", "octree", "features", "filters", "ml"]},
            "surface": {"requires": ["common", "search", "kdtree", "octree"] + qhull()},
            "registration": {"requires": ["common", "octree", "kdtree", "search", "sample_consensus", "features", "filters"]},
            "keypoints": {"requires": ["common", "search", "kdtree", "octree", "features", "filters"]},
            "tracking": {"requires": ["common", "search", "kdtree", "filters", "octree"]},
            "recognition": {"requires": ["common", "io", "search", "kdtree", "octree", "features", "filters", "registration", "sample_consensus", "ml"]},
            "stereo": {"requires": ["common", "io"]}
        }

    @property
    def _version_suffix(self):
        semver = Version(self.version)
        return "{}.{}".format(semver.major, semver.minor)

    def _lib_name(self, lib):
        if self.settings.compiler == "msvc" and self.settings.build_type == "Debug":
            return "pcl_{}d".format(lib)
        return "pcl_{}".format(lib)
    
    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "PCL"
        self.cpp_info.names["cmake_find_package_multi"] = "PCL"

        self.cpp_info.set_property("cmake_file_name", "PCL")
        self.cpp_info.set_property("cmake_module_file_name", "PCL")
        self.cpp_info.set_property("cmake_target_name", "PCL::PCL")

        def _update_components(components):
            for comp, values in components.items():
                self.cpp_info.components[comp].names["cmake_find_package"] = comp
                self.cpp_info.components[comp].names["cmake_find_package_multi"] = comp
                self.cpp_info.components[comp].set_property("cmake_file_name", comp)
                self.cpp_info.components[comp].set_property("cmake_module_file_name", comp)
                self.cpp_info.components[comp].set_property("cmake_target_name", f"PCL::{comp}")

                self.cpp_info.components[comp].names["pkg_config"] = "pcl_{}-{}".format(comp, self._version_suffix)
                self.cpp_info.components[comp].set_property("pkg_config_name", "pcl_{}-{}".format(comp, self._version_suffix))

                self.cpp_info.components[comp].includedirs = [os.path.join("include", "pcl-{}".format(self._version_suffix))]
                if not values.get("header_only", False):
                    libs = [comp] + values.get("extra_libs", [])
                    self.cpp_info.components[comp].libs = [self._lib_name(lib) for lib in libs]
                self.cpp_info.components[comp].requires = values["requires"]

        _update_components(self._pcl_lib_components)

        if not self.options.shared:
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["common"].system_libs.append("pthread")
            if self.options.with_openmp:
                if self.settings.os == "Linux":
                    if self.settings.compiler == "gcc":
                        self.cpp_info.components["common"].sharedlinkflags.append("-fopenmp")
                        self.cpp_info.components["common"].exelinkflags.append("-fopenmp")
                elif self.settings.os == "Windows":
                    if self.settings.compiler == "msvc":
                        self.cpp_info.components["common"].system_libs.append("delayimp")
                    elif self.settings.compiler == "gcc":
                        self.cpp_info.components["common"].system_libs.append("gomp")    

        if self.options.with_apps:
            self.cpp_info.components["apps"].libs = []
            self.cpp_info.components["apps"].requires = ["qt::qt"]
