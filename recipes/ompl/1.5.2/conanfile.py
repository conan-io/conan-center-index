from conans import ConanFile, tools, CMake
import os
import glob

BOOST_MODULES = ["system","filesystem","program_options","serialization","test"]
BOOST_UNUSED_MODULES = ["atomic","chrono","container","context","contract","coroutine","date_time","exception",
                        "fiber","graph","graph_parallel","iostreams","locale","log","math","mpi","python","random",
                        "regex","stacktrace","thread","timer","type_erasure","wave"]

class ConanOmpl(ConanFile):
    name = "ompl"
    version = "1.5.2"
    license = "BSD"
    homepage = "https://ompl.kavrakilab.org/"
    description = "OMPL, the Open Motion Planning Library, consists of many state-of-the-art sampling-based motion planning algorithms."
    url = "https://bitbucket.org/radalytica/conan-packages"
    author = "Mohamed Ghita (https://github.com/mohamedghita)"
    generators = "cmake_find_package", "cmake_paths", "cmake"
    BOOST_VERSION = "1.72.0"
    requires = "boost/{}".format(BOOST_VERSION), "eigen/3.3.9"

    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {"shared": [True, False], "run_tests": [True, False], "fPIC": [True, False],}
    default_options = {"shared": True, "run_tests": False, "fPIC": True}

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        boost_options = self.options["boost"]
        for module in BOOST_MODULES:
            setattr(boost_options, "without_{}".format(module), False)
        for module in BOOST_UNUSED_MODULES:
            setattr(boost_options, "without_{}".format(module), True)

    @property
    def _source_subfolder(self):
        return "ompl-{}".format(self.version)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

        tools.replace_in_file("{}/CMakeLists.txt".format(self._source_subfolder), 
                        "project(ompl VERSION {} LANGUAGES CXX)".format(self.version),
                        'project(ompl VERSION {} LANGUAGES CXX)\n'.format(self.version) +
                        'include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)\n' +
                        'conan_basic_setup(KEEP_RPATHS)\n' + 
                        'include(${CMAKE_BINARY_DIR}/conan_paths.cmake)\n')

        tools.replace_in_file("{}/CMakeLists.txt".format(self._source_subfolder), 
                        "find_package(Boost 1.58 QUIET REQUIRED COMPONENTS serialization filesystem system program_options)",
                        'find_package(Boost {} REQUIRED)\n'.format(self.BOOST_VERSION) +     
                        'set(Boost_SERIALIZATION_LIBRARY "${Boost_LIBRARIES_TARGETS}")\n' + 
                        'set(Boost_FILESYSTEM_LIBRARY "${Boost_LIBRARIES_TARGETS}")\n' + 
                        'set(Boost_SYSTEM_LIBRARY "${Boost_LIBRARIES_TARGETS}")\n' +
                        'set(Boost_LIBRARY_DIRS " ")')

        tools.replace_in_file("{}/CMakeLists.txt".format(self._source_subfolder), 
                "find_package(Eigen3 REQUIRED)", 
                'find_package(Eigen3 REQUIRED)\n' +
                'set(EIGEN3_INCLUDE_DIR ${Eigen3_INCLUDE_DIR})')

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["OMPL_BUILD_TESTS"] = self.options.run_tests
        cmake.definitions["OMPL_BUILD_DEMOS"] = self.options.run_tests

        ignored_packages = ["pypy","flann","ODE", "spot","MORSE","Triangle"]
        for pkg in ignored_packages:
            cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_{}".format(pkg)] = "ON" 

        disabled_options = ["BUILD_PYBINDINGS","BUILD_PYTESTS","REGISTRATION","VERSIONED_INSTALL"]
        for opt in disabled_options:
            cmake.definitions["OMPL_{}".format(opt)] = "OFF"

        cmake.configure(source_folder=os.path.join(self.build_folder, self._source_subfolder))
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        if self.options.run_tests:
            cmake.build()
            cmake.test()
        else:
            cmake.build(target="ompl")

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libs = ["ompl"]
        self.cpp_info.libdirs = ['lib']