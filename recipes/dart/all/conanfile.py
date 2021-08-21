from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class DartConan(ConanFile):
    name = "dart"
    homepage = "http://dartsim.github.io/"
    description = "Dynamic Animation and Robotics Toolkit"
    topics = ("robotics", "computer-animation", "simulation", "kinematics", "dynamics", "lie-group")
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-2-Clause"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "pkg_config", "cmake_find_package", "cmake_find_package_multi"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_utils": [True, False],
        #"with_imgui": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_utils": True,
        #"with_imgui": True,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "5",
            "apple-clang": "5.1",
        }
    
    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, "14")
        
        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("C++14 required. Your compiler is unknown, assuming it supports C++14.")
        elif tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("Requires C++14, which your compiler does not support.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

        tools.replace_in_file(os.path.join(self._source_subfolder, "dart", "utils", "CMakeLists.txt"),
                        'set(CMAKE_REQUIRED_INCLUDES "${Boost_INCLUDE_DIRS}")',
                        'set(CMAKE_REQUIRED_INCLUDES "${Boost_INCLUDE_DIRS}")\nmessage(">>>> Boost_INCLUDE_DIRS: ${Boost_INCLUDE_DIRS}")')


        # Do not build directories with tests, examples and tutorials
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                        "add_subdirectory(unittest",
                        "# add_subdirectory(unittest")

        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                        "add_subdirectory(examples",
                        "# add_subdirectory(examples")

        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                        "add_subdirectory(tutorials",
                        "# add_subdirectory(tutorials")

        # Do not try to find clang-format
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                        "find_program(\n  CLANG_FORMAT_EXECUTABLE\n  NAMES clang-format-6.0\n)",
                        "")

        # FIXME: Conan generator doesn't populate required vars to support COMPONENTS?!
        tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "DARTFindBoost.cmake"),
                        "COMPONENTS ${BOOST_REQUIRED_COMPONENTS}",
                        "")

    def requirements(self):
        self.requires("eigen/3.4.0")
        self.requires("libccd/2.1")
        self.requires("fcl/0.6.1")
        self.requires("assimp/5.0.1")
        self.requires("boost/1.76.0")
        self.requires("octomap/1.9.7")
        if self.options.with_utils:
            self.requires("tinyxml2/8.0.0")
        #if self.options.with_imgui:
        #    self.requires("imgui/1.83")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        #self._cmake.definitions["CMAKE_VERBOSE_MAKEFILE"] = True
        self._cmake.definitions["DART_VERBOSE"] = True
        self._cmake.definitions["EIGEN3_VERSION_STRING"] = self.deps_cpp_info["eigen"].version
        self._cmake.definitions["DART_BUILD_GUI_OSG"] = False
        self._cmake.definitions["DART_BUILD_DARTPY"] = False
        self._cmake.definitions["DART_BUILD_EXTRAS"] = False
        self._cmake.definitions["DART_BUILD_DARTPY"] = False
        self._cmake.definitions["DART_SKIP_DOXYGEN"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        os.unlink("BoostConfig.cmake")  # Boost - force FindBoost, because I need INCLUDE_DIRS without gen-expressions
        os.unlink("Findassimp.cmake")  # Library provides Findassimp with some convenient logic

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.components["external-imgui"].libs = ["dart-external-imgui"]
        self.cpp_info.components["external-lodepng"].libs = ["dart-external-lodepng"]
        self.cpp_info.components["external-odelcpsolver"].libs = ["dart-external-odelcpsolver"]
        
        # Steal component name 'dart'
        self.cpp_info.components["core"].names["cmake_find_package"] = "dart"
        self.cpp_info.components["core"].names["cmake_find_package_multi"] = "dart"
        self.cpp_info.components["core"].libs = ["dart"]
        self.cpp_info.components["core"].requires = ["eigen::eigen", "libccd::libccd", "fcl::fcl",
                                                     "assimp::assimp", "boost::headers", "boost::system", 
                                                     "boost::filesystem", "octomap::octomap",
                                                     "external-odelcpsolver"]

        if self.options.with_utils:
            self.cpp_info.components["utils"].libs = ["dart-utils"]
            self.cpp_info.components["utils"].requires = ["core", "tinyxml2::tinyxml2"]
