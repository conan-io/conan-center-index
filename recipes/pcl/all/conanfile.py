import shutil
import os.path

from conans import ConanFile, CMake, tools


class ConanRecipe(ConanFile):
    name = "pcl"
    description = "Point Cloud Library"
    license = "BSD-3-Clause"
    homepage = "https://pointclouds.org/"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tools": [True, False],
        "usb": [True, False],
        "png": [True, False],
        "qhull": [True, False],
        "cuda": [True, False],
        "vtk": [True, False],
        "pcap": [True, False],
        "opengl": [True, False],
        "openni": [True, False],
        "openni2": [True, False],
        "ensenso": [True, False],
        "davidsdk": [True, False],
        "dssdk": [True, False],
        "rssdk": [True, False],
        "kdtree": [True, False],
        "octree": [True, False],
        "search": [True, False],
        "sample_consensus": [True, False],
        "filters": [True, False],
        "twod": [True, False],
        "geometry": [True, False],
        "io": [True, False],
        "features": [True, False],
        "ml": [True, False],
        "segmentation": [True, False],
        "surface": [True, False],
        "registration": [True, False],
        "keypoints": [True, False],
        "tracking": [True, False],
        "recognition": [True, False],
        "stereo": [True, False]
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "tools": False,
        "boost:shared": True,
        "usb": False,
        "png": True,
        "qhull": True,
        "cuda": False,
        "vtk": False,
        "pcap": False,
        "opengl": True,
        "openni": False,
        "openni2": False,
        "ensenso": False,
        "davidsdk": False,
        "dssdk": False,
        "rssdk": False,
        "kdtree": True,
        "octree": True,
        "search": False,
        "sample_consensus": False,
        "filters": False,
        "twod": False,
        "geometry": True,
        "io": True,
        "features": False,
        "ml": True,
        "segmentation": True,
        "surface": True,
        "registration": True,
        "keypoints": False,
        "tracking": False,
        "recognition": False,
        "stereo": False
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
        if self.options.png:
            self.requires("libpng/[>1.6.36]")
        if self.options.qhull:
            self.requires("qhull/[>7.3.0]")
            self.options["qhull"].shared=False

    def configure(self):
        if self.options.registration:
            self.options.octree = True
            self.options.filters = True
            self.options.features = True
        if self.options.io:
            self.options.octree = True
        if self.options.filters:
            self.options.kdtree = True
            self.options.search = True
            self.options.sample_consensus = True
        if self.options.segmentation:
            self.options.ml = True
        if self.options.features:
            self.options.twod = True


    def _configure_cmake(self):
        cmake_definitions = {
            "PCL_BUILD_WITH_BOOST_DYNAMIC_LINKING_WIN32": self.options["boost"].shared,
        }

        pcl_config = {
            "EIGEN_ROOT": self.deps_cpp_info["eigen"].rootpath,
            "FLANN_ROOT": self.deps_cpp_info["flann"].rootpath,
            "BOOST_ROOT": self.deps_cpp_info["boost"].rootpath,
            "BUILD_tools": self.options.tools,
            "WITH_LIBUSB": self.options.usb,
            "WITH_PNG": self.options.png,
            "WITH_QHULL": self.options.qhull,
            "WITH_CUDA": self.options.cuda,
            "WITH_VTK": self.options.vtk,
            "WITH_PCAP": self.options.pcap,
            "WITH_OPENGL": self.options.opengl,
            "WITH_OPENNI": self.options.openni2,
            "WITH_OPENNI2": self.options.openni2,
            "WITH_ENSENSO": self.options.ensenso,
            "WITH_DAVIDSDK": self.options.davidsdk,
            "WITH_DSSDK": self.options.dssdk,
            "WITH_RSSDK": self.options.rssdk,
            "PCL_SHARED_LIBS": self.options.shared
        }
        pcl_features = {
            "BUILD_kdtree": self.options.kdtree,
            "BUILD_octree": self.options.octree,
            "BUILD_search": self.options.search,
            "BUILD_sample_consensus": self.options.sample_consensus,
            "BUILD_filters": self.options.filters,
            "BUILD_2d": self.options.twod,
            "BUILD_geometry": self.options.geometry,
            "BUILD_io": self.options.io,
            "BUILD_features": self.options.features,
            "BUILD_ml": self.options.ml,
            "BUILD_segmentation": self.options.segmentation,
            "BUILD_surface": self.options.surface,
            "BUILD_registration": self.options.registration,
            "BUILD_keypoints": self.options.keypoints,
            "BUILD_tracking": self.options.tracking,
            "BUILD_recognition": self.options.recognition,
            "BUILD_stereo": self.options.stereo
        }

        if self.options.png:
            pcl_config["LIBPNG_ROOT"] = self.deps_cpp_info["libpng"].rootpath
        if self.options.qhull:
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
