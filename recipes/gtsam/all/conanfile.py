import os
import stat
import shutil
from conans import ConanFile, tools, CMake

class gtsamConan(ConanFile):
    name = "gtsam"
    license = "BSD-2-Clause"
    homepage = "https://github.com/borglab/gtsam"
    url = "https://github.com/conan-io/conan-center-index"
    description = ("GTSAM is a library of C++ classes that implement\
                    smoothing and mapping (SAM) in robotics and vision")
    topics = ("conan", "gtsam", "mapping", "smoothing")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "USE_QUATERNIONS": [True, False],
               "POSE3_EXPMAP": [True, False],
               "ROT3_EXPMAP": [True, False],
               "ENABLE_CONSISTENCY_CHECKS": [True, False],
               "WITH_TBB": [True, False],
               "WITH_EIGEN_MKL": [True, False],
               "WITH_EIGEN_MKL_OPENMP": [True, False],
               "THROW_CHEIRALITY_EXCEPTION": [True, False],
               "ALLOW_DEPRECATED_SINCE_V4": [True, False],
               "TYPEDEF_POINTS_TO_VECTORS": [True, False],
               "SUPPORT_NESTED_DISSECTION": [True, False],
               "TANGENT_PREINTEGRATION": [True, False],
               "BUILD_WRAP": [True, False],
               "WRAP_SERIALIZATION": [True, False],
               "BUILD_UNSTABLE": [True, False],
               "DISABLE_NEW_TIMERS": [True, False],
               "BUILD_TYPE_POSTFIXES": [True, False],
               "Boost_USE_STATIC_LIBS": [True, False],
               "INSTALL_MATLAB_TOOLBOX": [True, False],
               "INSTALL_CYTHON_TOOLBOX": [True, False],
               "INSTALL_CPPUNITLITE": [True, False],
               "INSTALL_GEOGRAPHICLIB": [True, False]}

    default_options = {"shared": False,
                       "fPIC": True,
                        "USE_QUATERNIONS": False,
                        "POSE3_EXPMAP": False,
                        "ROT3_EXPMAP": False,
                        "ENABLE_CONSISTENCY_CHECKS": False,
                        "WITH_TBB": True,
                        "WITH_EIGEN_MKL": False,
                        "WITH_EIGEN_MKL_OPENMP": False,
                        "THROW_CHEIRALITY_EXCEPTION": True,
                        "ALLOW_DEPRECATED_SINCE_V4": True,
                        "TYPEDEF_POINTS_TO_VECTORS": False,
                        "SUPPORT_NESTED_DISSECTION": False,
                        "TANGENT_PREINTEGRATION": False,
                        "BUILD_WRAP": True,
                        "WRAP_SERIALIZATION": True,
                        "BUILD_UNSTABLE": True,
                        "DISABLE_NEW_TIMERS": False,
                        "BUILD_TYPE_POSTFIXES": True,
                        "Boost_USE_STATIC_LIBS": True,
                        "INSTALL_MATLAB_TOOLBOX": False,
                        "INSTALL_CYTHON_TOOLBOX": False,
                        "INSTALL_CPPUNITLITE": True,
                        "INSTALL_GEOGRAPHICLIB": False}
    generators = "cmake"
    exports_sources = ["patches/*","CMakeLists.txt"]
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _cmake = None

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.verbose = False
            self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
            self._cmake.definitions["GTSAM_USE_QUATERNIONS"] = self.options.USE_QUATERNIONS
            self._cmake.definitions["GTSAM_POSE3_EXPMAP"] = self.options.POSE3_EXPMAP
            self._cmake.definitions["GTSAM_ROT3_EXPMAP"] = self.options.ROT3_EXPMAP
            self._cmake.definitions["GTSAM_ENABLE_CONSISTENCY_CHECKS"] = self.options.ENABLE_CONSISTENCY_CHECKS
            self._cmake.definitions["GTSAM_WITH_TBB"] = self.options.WITH_TBB
            self._cmake.definitions["GTSAM_WITH_EIGEN_MKL"] = self.options.WITH_EIGEN_MKL
            self._cmake.definitions["GTSAM_WITH_EIGEN_MKL_OPENMP"] = self.options.WITH_EIGEN_MKL_OPENMP
            self._cmake.definitions["GTSAM_THROW_CHEIRALITY_EXCEPTION"] = self.options.THROW_CHEIRALITY_EXCEPTION
            self._cmake.definitions["GTSAM_ALLOW_DEPRECATED_SINCE_V4"] = self.options.ALLOW_DEPRECATED_SINCE_V4
            self._cmake.definitions["GTSAM_TYPEDEF_POINTS_TO_VECTORS"] = self.options.TYPEDEF_POINTS_TO_VECTORS
            self._cmake.definitions["GTSAM_SUPPORT_NESTED_DISSECTION"] = self.options.SUPPORT_NESTED_DISSECTION
            self._cmake.definitions["GTSAM_TANGENT_PREINTEGRATION"] = self.options.TANGENT_PREINTEGRATION
            self._cmake.definitions["GTSAM_BUILD_UNSTABLE"] = self.options.BUILD_UNSTABLE
            self._cmake.definitions["GTSAM_DISABLE_NEW_TIMERS"] = self.options.DISABLE_NEW_TIMERS
            self._cmake.definitions["GTSAM_BUILD_TYPE_POSTFIXES"] = self.options.BUILD_TYPE_POSTFIXES
            self._cmake.definitions["GTSAM_BUILD_TESTS"] = False
            self._cmake.definitions["Boost_USE_STATIC_LIBS"] = self.options.Boost_USE_STATIC_LIBS
            self._cmake.definitions["Boost_NO_SYSTEM_PATHS"] = True
            self._cmake.definitions["GTSAM_BUILD_DOCS"] = False
            self._cmake.definitions["GTSAM_BUILD_DOC_HTML"] = False
            self._cmake.definitions["GTSAM_BUILD_EXAMPLES_ALWAYS"] = False
            self._cmake.definitions["GTSAM_BUILD_WRAP"] = self.options.BUILD_WRAP
            self._cmake.definitions["GTSAM_WRAP_SERIALIZATION"] = self.options.WRAP_SERIALIZATION
            self._cmake.definitions["GTSAM_INSTALL_MATLAB_TOOLBOX"] = self.options.INSTALL_MATLAB_TOOLBOX
            self._cmake.definitions["GTSAM_INSTALL_CYTHON_TOOLBOX"] = self.options.INSTALL_CYTHON_TOOLBOX
            self._cmake.definitions["GTSAM_INSTALL_CPPUNITLITE"] = self.options.INSTALL_CPPUNITLITE
            self._cmake.definitions["GTSAM_INSTALL_GEOGRAPHICLIB"] = self.options.INSTALL_GEOGRAPHICLIB
            self._cmake.definitions["GTSAM_USE_SYSTEM_EIGEN"] = False
            self._cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._cmake

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.requires("boost/1.72.0")
        self.options["boost"].shared = not self.options.Boost_USE_STATIC_LIBS
        self.requires("eigen/3.3.7")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("LICENSE.BSD", src=self._source_subfolder, dst="licenses")
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)