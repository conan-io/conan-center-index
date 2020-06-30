import os
from glob import glob
from itertools import chain

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class PclConanRecipe(ConanFile):
    name = "pcl"
    description = "Point Cloud Library"
    license = "BSD-3-Clause"
    homepage = "https://pointclouds.org/"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("pointcloud", "computer-vision", "point-cloud")
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
        "with_tools": False
    }
    requires = ("boost/1.70.0",
                "eigen/3.3.7",
                "flann/1.9.1",
                "libpng/1.6.37",
                "opengl/system",
                "qhull/7.3.2")
    generators = ["cmake", "cmake_find_package"]
    exports = ["CMakeLists.txt"]
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("pcl-pcl-{}".format(self.version), self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if (tools.msvs_toolset(self) == "v140" or
                self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version) < "15"):
            raise ConanInvalidConfiguration("Unsupported Visual Studio Compiler or Toolset")
        minimal_cpp_standard = "14"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)
        minimal_version = {
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "10",
            "Visual Studio": "14"
        }
        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warn(
                "%s recipe lacks information about the %s compiler standard version support" % (self.name, compiler))
            self.output.warn(
                "%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))
            return
        version = tools.Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            raise ConanInvalidConfiguration("%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

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

        self._cmake = CMake(self)
        self._cmake.definitions.update(cmake_definitions)
        self._cmake.definitions.update(pcl_config)
        self._cmake.definitions.update(pcl_features)
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _remove_vs_runtime_files(self):
        patterns = [os.path.join(self.package_folder, "bin", pattern) for pattern in ["msvcp*.dll", "vcruntime*.dll", "concrt*.dll"]]
        runtime_files = chain.from_iterable(glob(pattern) for pattern in patterns)
        for runtime_file in runtime_files:
            try:
                os.remove(runtime_file)
            except Exception as ex:
                self.output.warn("Could not remove vs runtime file {}, {}".format(runtime_file, ex))

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        if self.settings.os == "Windows":
            self._remove_vs_runtime_files()

        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        semver = tools.Version(self.version)
        self.cpp_info.includedirs = ["include/pcl-{}.{}".format(semver.major, semver.minor)]
        self.cpp_info.libs = tools.collect_libs(self)
