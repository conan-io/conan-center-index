import os
from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration

class ceressolverConan(ConanFile):
    name = "ceres-solver"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://ceres-solver.org/"
    description = ("Ceres Solver is an open source C++ library for modeling\
                    and solving large, complicated optimization problems")
    topics = ("optimization","Non-linear Least Squares")
    settings = "os", "arch", "compiler", "build_type"
    generators = ["cmake"]
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "use_glog":  [True, False], #TODO Set to true once gflags with nothreads=False binaries are available. Using MINILOG has a big performance drawback.
               "use_gflags": [True, False],
               "use_custom_blas": [True, False],
               "use_eigen_sparse": [True, False],
               "use_TBB": [True, False],
               "use_CXX11_threads": [True, False],
               "use_CXX11": [True, False],
               "use_schur_specializations": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "use_glog": False,
                       "use_gflags": False,
                       "use_custom_blas": True,
                       "use_eigen_sparse": True,
                       "use_TBB": False,
                       "use_CXX11_threads": False,
                       "use_CXX11": False,
                       "use_schur_specializations": True}
    exports_sources = ["CMakeLists.txt","patches/*"]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    _cmake = None

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if tools.Version(self.version) >= "2.0":
            del self.options.use_CXX11_threads
            del self.options.use_CXX11

    def _check_cxx14_supported(self):
        min_compiler_version = {
            "gcc": "5",
            "Visual Studio": "14",
            "clang": "5",
            "apple-clang": "5",
        }.get(str(self.settings.compiler))
        if not min_compiler_version:
            self.output.warn("Unknown compiler. Presuming it supports c++14.")
        elif tools.Version(self.settings.compiler.version) < min_compiler_version:
            raise ConanInvalidConfiguration("Current compiler version does not support c++14")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.build_type == "Debug" and self.options.use_glog:
            raise ConanInvalidConfiguration("Ceres-solver only links against the release version of glog")
        if self.options.use_glog and not self.options.use_gflags: #At this stage we can't check the value of self.options["glog"].with_gflags so we asume it is true because is the default value
            raise ConanInvalidConfiguration("To depend on glog built with gflags (Default behavior) set use_gflags=True, otherwise Ceres may fail to link due to missing gflags symbols.")
        if tools.Version(self.version) >= "2.0":
            # 1.x uses ceres-solver specific FindXXX.cmake modules
            self.generators.append("cmake_find_package")
            if self.settings.compiler.cppstd:
                tools.check_min_cppstd(self, 14)
            self._check_cxx14_supported()

    def requirements(self):
        self.requires("eigen/3.3.8")
        if self.options.use_glog:
            self.requires("glog/0.4.0")
        if self.options.use_gflags:
            self.requires("gflags/2.2.2")
            self.options["gflags"].nothreads = False
        if self.options.use_TBB:
            self.requires("tbb/2020.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)       #You can check what these flags do in http://ceres-solver.org/installation.html
        self._cmake.definitions["LIB_SUFFIX"] = ""
        self._cmake.definitions["GFLAGS"] = self.options.use_gflags
        self._cmake.definitions["BUILD_EXAMPLES"] = False           #Requires gflags
        self._cmake.definitions["BUILD_TESTING"] = False            #Requires gflags
        self._cmake.definitions["BUILD_DOCUMENTATION"] = False      #Requires python modules Sphinx and sphinx-rtd-theme
        self._cmake.definitions["CUSTOM_BLAS"] = self.options.use_custom_blas
        self._cmake.definitions["GLOG_PREFER_EXPORTED_GLOG_CMAKE_CONFIGURATION"] = False      #Set to false to Force CMake to use the conan-generated dependencies
        self._cmake.definitions["EIGENSPARSE"] = self.options.use_eigen_sparse
        self._cmake.definitions["SUITESPARSE"] = False  #Optional. Not supported right now because SuiteSparse is not part of conan-index
        self._cmake.definitions["LAPACK"] = False       #Optional. Not supported right now because LAPACK is not part of conan-index
        self._cmake.definitions["CXSPARSE"] = False     #Optional. Not supported right now because CXSSPARSE is not part of conan-index
        self._cmake.definitions["MINIGLOG"] = not self.options.use_glog
        if not self.options.use_TBB:
            self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_TBB"] = True
        if tools.Version(self.version) < "2.0":
            self._cmake.definitions["TBB"] = self.options.use_TBB
            self._cmake.definitions["OPENMP"] = False
            self._cmake.definitions["EIGEN_PREFER_EXPORTED_EIGEN_CMAKE_CONFIGURATION"] = False    #Set to false to Force CMake to use the conan-generated dependencies
            self._cmake.definitions["GFLAGS_PREFER_EXPORTED_GFLAGS_CMAKE_CONFIGURATION"] = False  #Set to false to Force CMake to use the conan-generated dependencies
            self._cmake.definitions["CXX11_THREADS"] = self.options.use_CXX11_threads
            self._cmake.definitions["CXX11"] = self.options.use_CXX11
        self._cmake.definitions["SCHUR_SPECIALIZATIONS"] = self.options.use_schur_specializations
        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["MSVC_USE_STATIC_CRT"] = str(self.settings.compiler.runtime) == "MT" or str(self.settings.compiler.runtime) == "MTd"
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "CMake"))

    def package_info(self):
        libsuffix = ""
        if self.settings.build_type == "Debug":
            libsuffix = "-debug"
        self.cpp_info.names["cmake_find_package"] = "Ceres"
        self.cpp_info.names["cmake_find_package_multi"] = "Ceres"
        self.cpp_info.components["ceres"].libs = ["ceres{}".format(libsuffix)]
        self.cpp_info.components["ceres"].includedirs = ["include", os.path.join("include","ceres")]
        if not self.options.use_glog:
            self.cpp_info.components["ceres"].includedirs.append(os.path.join("include","ceres", "internal", "miniglog"))
        if self.settings.os == "Linux":
            if self.options.get_safe("use_CXX11_threads", True):
                self.cpp_info.components["ceres"].system_libs.append("pthread")
        elif tools.is_apple_os(self.settings.os):
            if tools.Version(self.version) >= "2":
                self.cpp_info.components["ceres"].frameworks = ["Accelerate"]
        self.cpp_info.components["ceres"].requires = ["eigen::eigen"]
        if self.options.use_glog:
            self.cpp_info.components["ceres"].requires.append("glog::glog")
        if self.options.use_gflags:
            self.cpp_info.components["ceres"].requires.append("gflags::gflags")
        if self.options.use_TBB:
            self.cpp_info.components["ceres"].requires.append("tbb::tbb")
        libcxx = tools.stdcpp_library(self)
        if libcxx:
            self.cpp_info.components["ceres"].system_libs.append(libcxx)
