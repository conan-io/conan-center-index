from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, rm
from conan.tools.gnu import PkgConfigDeps
from conan.tools.scm import Version
from conan.tools.system import package_manager
import os

required_conan_version = ">=1.53.0"


class PclConan(ConanFile):
    name = "pcl"
    description = "The Point Cloud Library (PCL) is a standalone, large-scale, open project for 2D/3D image and point cloud processing."
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
        "with_opengl": True,
        "with_tools": False,
        "with_apps": False,
    }

    short_paths = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10",
            "msvc": "191",
            "Visual Studio": "15",
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
            # TODO: add vtk/system package?
            package_manager.Apt(self).install(["libvtk-dev"])
            package_manager.Dnf(self).install(["vtk-devel"])
            if self.settings.os == "Windows":
                self.output.warn("VTK must be installed manually on Windows.")

    def requirements(self):
        self.requires("zlib/1.2.13")
        # Boost is used in public PCL headers here:
        # https://github.com/PointCloudLibrary/pcl/blob/pcl-1.13.1/common/include/pcl/point_struct_traits.h#L40-L46
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
            self.requires("freeglut/3.4.0")
            self.requires("glew/2.2.0")
        # TODO:
        # self.requires("vtk/9.x.x")
        # self.requires("openni/x.x.x")
        # self.requires("openni2/x.x.x")
        # self.requires("ensenso/x.x.x")
        # self.requires("davidsdk/x.x.x")
        # self.requires("dssdk/x.x.x")
        # self.requires("rssdk/x.x.x")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["PCL_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["WITH_CUDA"] = self.options.with_cuda
        tc.cache_variables["WITH_LIBUSB"] = self.options.with_libusb
        tc.cache_variables["WITH_OPENGL"] = self.options.with_opengl
        tc.cache_variables["WITH_OPENMP"] = self.options.with_openmp
        tc.cache_variables["WITH_PCAP"] = self.options.with_pcap
        tc.cache_variables["WITH_PNG"] = self.options.with_png
        tc.cache_variables["WITH_QHULL"] = self.options.with_qhull
        tc.cache_variables["WITH_QT"] = self.options.with_apps
        tc.cache_variables["WITH_VTK"] = self.options.with_vtk
        tc.cache_variables["WITH_SYSTEM_ZLIB"] = True
        tc.cache_variables["BUILD_tools"] = self.options.with_tools
        tc.cache_variables["BUILD_apps"] = self.options.with_apps
        tc.cache_variables["BUILD_examples"] = False
        tc.cache_variables["PCL_ONLY_CORE_POINT_TYPES"] = True
        # The default False setting breaks OpenGL detection in CMake
        tc.cache_variables["PCL_ALLOW_BOTH_SHARED_AND_STATIC_DEPENDENCIES"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("eigen", "cmake_file_name", "EIGEN")
        deps.set_property("flann", "cmake_file_name", "FLANN")
        deps.set_property("flann", "cmake_target_name", "FLANN::FLANN")
        deps.set_property("pcap", "cmake_file_name", "PCAP")
        deps.set_property("qhull", "cmake_file_name", "QHULL")
        deps.set_property("qhull", "cmake_target_name", "QHULL::QHULL")
        deps.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        for mod in ["Eigen", "FLANN", "GLEW", "Pcap", "Qhull", "libusb"]:
            os.remove(os.path.join(self.source_folder, "cmake", "Modules", f"Find{mod}.cmake"))

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)

        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        # Remove MSVC runtime libraries
        for dll_pattern_to_remove in ["concrt*.dll", "msvcp*.dll", "vcruntime*.dll"]:
            rm(self, dll_pattern_to_remove, os.path.join(self.package_folder, "bin"))

    @property
    def _version_suffix(self):
        semver = Version(self.version)
        return f"{semver.major}.{semver.minor}"

    def _lib_name(self, lib):
        if self.settings.compiler == "msvc" and self.settings.build_type == "Debug":
            return f"pcl_{lib}d"
        return f"pcl_{lib}"

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "PCL"
        self.cpp_info.names["cmake_find_package_multi"] = "PCL"

        self.cpp_info.set_property("cmake_file_name", "PCL")
        self.cpp_info.set_property("cmake_module_file_name", "PCL")
        self.cpp_info.set_property("cmake_target_name", "PCL::PCL")

        def _add_component(comp, requires, *, extra_libs=None, header_only=False):
            self.cpp_info.components[comp].names["cmake_find_package"] = comp
            self.cpp_info.components[comp].names["cmake_find_package_multi"] = comp
            self.cpp_info.components[comp].set_property("cmake_file_name", comp)
            self.cpp_info.components[comp].set_property("cmake_module_file_name", comp)
            self.cpp_info.components[comp].set_property("cmake_target_name", f"PCL::{comp}")
            self.cpp_info.components[comp].set_property("pkg_config_name", f"pcl_{comp}-{self._version_suffix}")
            self.cpp_info.components[comp].includedirs = [os.path.join("include", f"pcl-{self._version_suffix}")]
            if not header_only:
                libs = [comp]
                if extra_libs:
                    libs += extra_libs
                self.cpp_info.components[comp].libs = [self._lib_name(lib) for lib in libs]
            self.cpp_info.components[comp].requires = ["common"] + requires

        def usb():
            return ["libusb::libusb"] if self.options.with_libusb else []
        def png():
            return ["libpng::libpng"] if self.options.with_png else []
        def qhull():
            return ["qhull::qhull"] if self.options.with_qhull else []

        _add_component("common", ["eigen::eigen3", "boost::boost"])
        _add_component("kdtree", ["flann::flann"])
        _add_component("octree", [])
        _add_component("search", ["kdtree", "octree", "flann::flann"])
        _add_component("sample_consensus", ["search"])
        _add_component("filters", ["sample_consensus", "search", "kdtree", "octree"])
        _add_component("2d", ["filters"], header_only=True)
        _add_component("geometry", [], header_only=True)
        _add_component("io", ["octree", "zlib::zlib"] + png() + usb(), extra_libs=["io_ply"])
        _add_component("features", ["search", "kdtree", "octree", "filters", "2d"])
        _add_component("ml", [])
        _add_component("segmentation", ["geometry", "search", "sample_consensus", "kdtree", "octree", "features", "filters", "ml"])
        _add_component("surface", ["search", "kdtree", "octree"] + qhull())
        _add_component("registration", ["octree", "kdtree", "search", "sample_consensus", "features", "filters"])
        _add_component("keypoints", ["search", "kdtree", "octree", "features", "filters"])
        _add_component("tracking", ["search", "kdtree", "filters", "octree"])
        _add_component("recognition", ["io", "search", "kdtree", "octree", "features", "filters", "registration", "sample_consensus", "ml"])
        _add_component("stereo", ["io"])


        if not self.options.shared:
            common = self.cpp_info.components["common"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                common.system_libs.append("pthread")
            if self.options.with_openmp:
                if self.settings.os == "Linux":
                    if self.settings.compiler == "gcc":
                        common.sharedlinkflags.append("-fopenmp")
                        common.exelinkflags.append("-fopenmp")
                elif self.settings.os == "Windows":
                    if self.settings.compiler == "msvc":
                        common.system_libs.append("delayimp")
                    elif self.settings.compiler == "gcc":
                        common.system_libs.append("gomp")

        if self.options.with_apps:
            self.cpp_info.components["apps"].libs = []
            self.cpp_info.components["apps"].requires = ["qt::qt"]
