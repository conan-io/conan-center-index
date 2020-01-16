import os
import stat
import shutil
from conans import ConanFile, tools, CMake

class gtsamConan(ConanFile):
    name = "gtsam"
    license = "BSD-3-Clause"
    homepage = "https://github.com/borglab/gtsam"
    url = "https://github.com/conan-io/conan-center-index"
    description = ("GTSAM is a library of C++ classes that implement\
                    smoothing and mapping (SAM) in robotics and vision")
    topics = ("conan", "gtsam", "mapping", "smoothing")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "use_quaternions": [True, False],
               "pose3_expmap": [True, False],
               "rot3_expmap": [True, False],
               "enable_consistency_checks": [True, False],
               "with_TBB": [True, False],
               "with_eigen_MKL": [True, False],
               "with_eigen_MKL_OPENMP": [True, False],
               "throw_cheirality_exception": [True, False],
               "allow_deprecated_since_V4": [True, False],
               "typedef_points_to_vectors": [True, False],
               "support_nested_dissection": [True, False],
               "tangent_preintegration": [True, False],
               "build_wrap": [True, False],
               "wrap_serialization": [True, False],
               "build_unstable": [True, False],
               "disable_new_timers": [True, False],
               "build_type_postfixes": [True, False],
               "install_matlab_toolbox": [True, False],
               "install_cython_toolbox": [True, False],
               "install_cppunitlite": [True, False],
               "install_geographiclib": [True, False]}

    default_options = {"shared": False,
                       "fPIC": True,
                        "use_quaternions": False,
                        "pose3_expmap": False,
                        "rot3_expmap": False,
                        "enable_consistency_checks": False,
                        "with_TBB": True,
                        "with_eigen_MKL": False,
                        "with_eigen_MKL_OPENMP": False,
                        "throw_cheirality_exception": True,
                        "allow_deprecated_since_V4": True,
                        "typedef_points_to_vectors": False,
                        "support_nested_dissection": False,
                        "tangent_preintegration": False,
                        "build_wrap": True,
                        "wrap_serialization": True,
                        "build_unstable": True,
                        "disable_new_timers": False,
                        "build_type_postfixes": True,
                        "install_matlab_toolbox": False,
                        "install_cython_toolbox": False,
                        "install_cppunitlite": True,
                        "install_geographiclib": False}
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
            self._cmake.definitions["GTSAM_USE_QUATERNIONS"] = self.options.use_quaternions
            self._cmake.definitions["GTSAM_POSE3_EXPMAP"] = self.options.pose3_expmap
            self._cmake.definitions["GTSAM_ROT3_EXPMAP"] = self.options.rot3_expmap
            self._cmake.definitions["GTSAM_ENABLE_CONSISTENCY_CHECKS"] = self.options.enable_consistency_checks
            self._cmake.definitions["GTSAM_WITH_TBB"] = self.options.with_TBB
            self._cmake.definitions["GTSAM_WITH_EIGEN_MKL"] = self.options.with_eigen_MKL
            self._cmake.definitions["GTSAM_WITH_EIGEN_MKL_OPENMP"] = self.options.with_eigen_MKL_OPENMP
            self._cmake.definitions["GTSAM_THROW_CHEIRALITY_EXCEPTION"] = self.options.throw_cheirality_exception
            self._cmake.definitions["GTSAM_ALLOW_DEPRECATED_SINCE_V4"] = self.options.allow_deprecated_since_V4
            self._cmake.definitions["GTSAM_TYPEDEF_POINTS_TO_VECTORS"] = self.options.typedef_points_to_vectors
            self._cmake.definitions["GTSAM_SUPPORT_NESTED_DISSECTION"] = self.options.support_nested_dissection
            self._cmake.definitions["GTSAM_TANGENT_PREINTEGRATION"] = self.options.tangent_preintegration
            self._cmake.definitions["GTSAM_BUILD_UNSTABLE"] = self.options.build_unstable
            self._cmake.definitions["GTSAM_DISABLE_NEW_TIMERS"] = self.options.disable_new_timers
            self._cmake.definitions["GTSAM_BUILD_TYPE_POSTFIXES"] = self.options.build_type_postfixes
            self._cmake.definitions["GTSAM_BUILD_TESTS"] = False
            self._cmake.definitions["Boost_NO_SYSTEM_PATHS"] = True
            self._cmake.definitions["GTSAM_BUILD_DOCS"] = False
            self._cmake.definitions["GTSAM_BUILD_DOC_HTML"] = False
            self._cmake.definitions["GTSAM_BUILD_EXAMPLES_ALWAYS"] = False
            self._cmake.definitions["GTSAM_BUILD_WRAP"] = self.options.build_wrap
            self._cmake.definitions["GTSAM_WRAP_SERIALIZATION"] = self.options.wrap_serialization
            self._cmake.definitions["GTSAM_INSTALL_MATLAB_TOOLBOX"] = self.options.install_matlab_toolbox
            self._cmake.definitions["GTSAM_INSTALL_CYTHON_TOOLBOX"] = self.options.install_cython_toolbox
            self._cmake.definitions["GTSAM_INSTALL_CPPUNITLITE"] = self.options.install_cppunitlite
            self._cmake.definitions["GTSAM_INSTALL_GEOGRAPHICLIB"] = self.options.install_geographiclib
            self._cmake.definitions["GTSAM_USE_SYSTEM_EIGEN"] = False
            self._cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._cmake

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.requires("boost/1.72.0")
        self.options["boost"].shared = False
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