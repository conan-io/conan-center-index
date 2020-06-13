import shutil
import os.path

from conans import ConanFile, CMake, tools


class PclConanRecipe(ConanFile):
    name = "pcl"
    description = "Point Cloud Library"
    license = "BSD-3-Clause"
    homepage = "https://pointclouds.org/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_cuda": [True, False],
        "with_davidsdk": [True, False],
        "with_dssdk": [True, False],
        "with_ensenso": [True, False],
        "with_opengl": [True, False],
        "with_openni": [True, False],
        "with_openni2": [True, False],
        "with_pcap": [True, False],
        "with_png": [True, False],
        "with_qhull": [True, False],
        "with_rssdk": [True, False],
        "with_tools": [True, False],
        "with_usb": [True, False],
        "with_vtk": [True, False],
        "module_2d": [True, False],
        "module_features": [True, False],
        "module_filters": [True, False],
        "module_geometry": [True, False],
        "module_io": [True, False],
        "module_kdtree": [True, False],
        "module_keypoints": [True, False],
        "module_ml": [True, False],
        "module_octree": [True, False],
        "module_registration": [True, False],
        "module_sample_consensus": [True, False],
        "module_search": [True, False],
        "module_segmentation": [True, False],
        "module_stereo": [True, False],
        "module_surface": [True, False],
        "module_tracking": [True, False],
        "module_recognition": [True, False]
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "boost:shared": True,
        "with_cuda": False,
        "with_davidsdk": False,
        "with_dssdk": False,
        "with_ensenso": False,
        "with_opengl": True,
        "with_openni": False,
        "with_openni2": False,
        "with_qhull": True,
        "with_pcap": False,
        "with_png": True,
        "with_rssdk": False,
        "with_tools": False,
        "with_usb": False,
        "with_vtk": False,
        "module_2d": False,
        "module_features": False,
        "module_filters": False,
        "module_geometry": True,
        "module_io": True,
        "module_kdtree": True,
        "module_keypoints": False,
        "module_ml": True,
        "module_octree": True,
        "module_recognition": False,
        "module_registration": True,
        "module_sample_consensus": False,
        "module_search": False,
        "module_segmentation": True,
        "module_stereo": False,
        "module_surface": True,
        "module_tracking": False
    }
    requires = ("boost/[>1.69.0]",
                "eigen/[>3.3.5]",
                "flann/[>1.9.0]")
    generators = "cmake"
    exports = ["CMakeLists.txt"]

    @property
    def _major_minor_version(self):
        major, minor, patch = self.version.split(".")
        return ".".join([major, minor])

    @property
    def _source_subfolder(self):
        return f"pcl-pcl-{self.version}"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        tools.replace_in_file("CMakeLists.txt", "add_subdirectory(pcl)", f"add_subdirectory({self._source_subfolder})")

    def requirements(self):
        if self.options.with_png:
            self.requires("libpng/[>1.6.36]")
        if self.options.with_qhull:
            self.requires("qhull/[>7.3.0]")
            self.options["qhull"].shared = False
        if self.options.with_opengl:
            self.requires("opengl/system")

    def configure(self):
        if self.options.module_registration:
            self.options.module_octree = True
            self.options.module_filters = True
            self.options.module_features = True
            self.options.module_2d = True
        if self.options.module_io:
            self.options.module_octree = True
        if self.options.module_filters:
            self.options.module_kdtree = True
            self.options.module_search = True
            self.options.module_sample_consensus = True
        if self.options.module_segmentation:
            self.options.module_ml = True
        if self.options.module_features:
            self.options.module_2d = True

    def _configure_cmake(self):
        cmake_definitions = {
            "PCL_BUILD_WITH_BOOST_DYNAMIC_LINKING_WIN32": self.options["boost"].shared
        }

        pcl_config = {
            "EIGEN_ROOT": self.deps_cpp_info["eigen"].rootpath,
            "FLANN_ROOT": self.deps_cpp_info["flann"].rootpath,
            "BOOST_ROOT": self.deps_cpp_info["boost"].rootpath,
            "BUILD_tools": self.options.with_tools,
            "WITH_LIBUSB": self.options.with_usb,
            "WITH_PNG": self.options.with_png,
            "WITH_QHULL": self.options.with_qhull,
            "WITH_CUDA": self.options.with_cuda,
            "WITH_VTK": self.options.with_vtk,
            "WITH_PCAP": self.options.with_pcap,
            "WITH_OPENGL": self.options.with_opengl,
            "WITH_OPENNI": self.options.with_openni,
            "WITH_OPENNI2": self.options.with_openni2,
            "WITH_ENSENSO": self.options.with_ensenso,
            "WITH_DAVIDSDK": self.options.with_davidsdk,
            "WITH_DSSDK": self.options.with_dssdk,
            "WITH_RSSDK": self.options.with_rssdk,
            "PCL_SHARED_LIBS": self.options.shared,
            "FLANN_USE_STATIC": not self.options["flann"].shared
        }
        pcl_features = {
            "BUILD_kdtree": self.options.module_kdtree,
            "BUILD_octree": self.options.module_octree,
            "BUILD_search": self.options.module_search,
            "BUILD_sample_consensus": self.options.module_sample_consensus,
            "BUILD_filters": self.options.module_filters,
            "BUILD_2d": self.options.module_2d,
            "BUILD_geometry": self.options.module_geometry,
            "BUILD_io": self.options.module_io,
            "BUILD_features": self.options.module_features,
            "BUILD_ml": self.options.module_ml,
            "BUILD_segmentation": self.options.module_segmentation,
            "BUILD_surface": self.options.module_surface,
            "BUILD_module_registration": self.options.module_registration,
            "BUILD_module_keypoints": self.options.module_keypoints,
            "BUILD_module_tracking": self.options.module_tracking,
            "BUILD_recognition": self.options.module_recognition,
            "BUILD_stereo": self.options.module_stereo
        }

        if self.options.with_png:
            pcl_config["LIBPNG_ROOT"] = self.deps_cpp_info["libpng"].rootpath
        if self.options.with_qhull:
            pcl_config["QHULL_ROOT"] = self.deps_cpp_info["qhull"].rootpath
            pcl_config["QHULL_USE_STATIC"] = True

        cmake = CMake(self)
        cmake.definitions.update(cmake_definitions)
        cmake.definitions.update(pcl_config)
        cmake.definitions.update(pcl_features)
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        shutil.rmtree(os.path.join(self.package_folder, "share"))
        shutil.rmtree(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.includedirs = [f"include/pcl-{self._major_minor_version}"]
        self.cpp_info.libs = tools.collect_libs(self)
