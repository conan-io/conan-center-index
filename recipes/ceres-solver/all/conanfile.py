import os
from conans import ConanFile, tools, CMake

class ceressolverConan(ConanFile):
    name = "ceres-solver"
    license = "	BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://ceres-solver.org/r"
    description = ("Ceres Solver is an open source C++ library for modeling\
                    and solving large, complicated optimization problems")
    topics = ("optimization","Non-linear Least Squares")
    settings = "os", "arch", "compiler", "build_type"
    generators = ["cmake"]
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "use_glog": [True, False],
               "use_gflags": [True, False],
               "use_custom_blas": [True, False],
               "use_eigen_sparse": [True, False],
               "use_TBB": [True, False],
               "use_CXX11_threads": [True, False],
               "use_CXX11": [True, False],
               "use_schur_specializations": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "use_glog": True,
                       "use_gflags": True,
                       "use_custom_blas": True,
                       "use_eigen_sparse": True,
                       "use_TBB": False,
                       "use_CXX11_threads": False,
                       "use_CXX11": False,
                       "use_schur_specializations": True}
    exports_sources = ["CMakeLists.txt","patches/*"]
    _source_subfolder = "source_subfolder"
    _cmake = None

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)       #You can check what these flags do in http://ceres-solver.org/installation.html
            self._cmake.definitions["GFLAGS"] = self.options.use_gflags
            self._cmake.definitions["BUILD_EXAMPLES"] = False           #Requires gflags
            self._cmake.definitions["BUILD_TESTING"] = False            #Requires gflags
            self._cmake.definitions["BUILD_DOCUMENTATION"] = False      #Requires python modules Sphinx and sphinx-rtd-theme
            self._cmake.definitions["CUSTOM_BLAS"] = self.options.use_custom_blas
            self._cmake.definitions["EIGEN_PREFER_EXPORTED_EIGEN_CMAKE_CONFIGURATION"] = False    #Set to false to Force CMake to use the conan-generated dependencies
            self._cmake.definitions["GLOG_PREFER_EXPORTED_GLOG_CMAKE_CONFIGURATION"] = False      #Set to false to Force CMake to use the conan-generated dependencies
            self._cmake.definitions["GFLAGS_PREFER_EXPORTED_GFLAGS_CMAKE_CONFIGURATION"] = False  #Set to false to Force CMake to use the conan-generated dependencies
            self._cmake.definitions["EIGENSPARSE"] = self.options.use_eigen_sparse
            self._cmake.definitions["SUITESPARSE"] = False  #Optional. Not sufpported right now because SuiteSparse is not part of conan-index
            self._cmake.definitions["LAPACK"] = False       #Optional. Not supported right now because LAPACK is not part of conan-index
            self._cmake.definitions["OPENMP"] = False
            self._cmake.definitions["CXSPARSE"] = False     #Optional. Not supported right now because CXSSPARSE is not part of conan-index
            self._cmake.definitions["MINIGLOG"] = not self.options.use_glog
            self._cmake.definitions["TBB"] = self.options.use_TBB
            self._cmake.definitions["CXX11_THREADS"] = self.options.use_CXX11_threads
            self._cmake.definitions["CXX11"] = self.options.use_CXX11
            self._cmake.definitions["SCHUR_SPECIALIZATIONS"] = self.options.use_schur_specializations
            self._cmake.configure()
        return self._cmake

    def requirements(self):
        self.requires.add("eigen/3.3.7")
        if self.options.use_glog:
            self.requires.add("glog/0.4.0")
        if self.options.use_gflags:
            self.requires.add("gflags/2.2.2")
            self.options["gflags"].nothreads = False
        if self.options.use_TBB:
            self.requires.add("tbb/2020.0")

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

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
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = ["include",os.path.join("include","ceres")]
