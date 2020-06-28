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
        "with_tools": [True, False]
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "with_cuda": False,
        "with_tools": False,
        "qhull:shared": False
    }
    requires = ("boost/1.70.0",
                "eigen/3.3.7",
                "flann/1.9.1",
                "libpng/1.6.37",
                "qhull/7.3.2")
    generators = ["cmake", "cmake_find_package"]
    exports = ["CMakeLists.txt"]

    @property
    def _source_subfolder(self):
        return "pcl-pcl-{}".format(self.version)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        tools.check_min_cppstd(self, "14")

    def _configure_cmake(self):
        cmake_definitions = {
            "CONAN_PCL_VERSION": self.version,
            "PCL_BUILD_WITH_BOOST_DYNAMIC_LINKING_WIN32": self.options["boost"].shared
        }

        pcl_config = {
            "BUILD_tools": self.options.with_tools,
            "WITH_LIBUSB": False,
            "WITH_PNG": True,
            "WITH_QHULL": True,
            "WITH_CUDA": self.options.with_cuda,
            "WITH_VTK": False,
            "WITH_PCAP": False,
            "WITH_OPENGL": True,
            "WITH_OPENNI": False,
            "WITH_OPENNI2": False,
            "WITH_ENSENSO": False,
            "WITH_DAVIDSDK": False,
            "WITH_DSSDK": False,
            "WITH_RSSDK": False,
            "PCL_SHARED_LIBS": self.options.shared,
            "FLANN_USE_STATIC": not self.options["flann"].shared,
            "QHULL_USE_STATIC": not self.options["qhull"].shared
        }
        pcl_features = {
            "BUILD_kdtree": True,
            "BUILD_octree": True,
            "BUILD_search": True,
            "BUILD_sample_consensus": True,
            "BUILD_filters": True,
            "BUILD_2d": True,
            "BUILD_geometry": True,
            "BUILD_io": True,
            "BUILD_features": True,
            "BUILD_ml": True,
            "BUILD_segmentation": True,
            "BUILD_surface": True,
            "BUILD_module_registration": True,
            "BUILD_module_keypoints": True,
            "BUILD_module_tracking": True,
            "BUILD_recognition": True,
            "BUILD_stereo": True,
        }

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
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        semver = tools.Version(self.version)
        self.cpp_info.includedirs = ["include/pcl-{}.{}".format(semver.major, semver.minor)]
        self.cpp_info.libs = tools.collect_libs(self)
