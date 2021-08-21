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
        "with_gui": [True, False],
        "with_gui_osg": [True, False],
        "with_optimizer_ipopt": [True, False],
        "with_optimizer_nlopt": [True, False],
        "with_optimizer_pagmo": [True, False],
        "with_collision_ode": [True, False],
        "with_collision_bullet": [True, False],
        "with_planning": [True, False],
        #"with_imgui": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_utils": True,
        "with_gui": True,
        "with_gui_osg": True,
        "with_optimizer_ipopt": False,
        "with_optimizer_nlopt": True,
        "with_optimizer_pagmo": True,
        "with_collision_ode": False,
        "with_collision_bullet": True,
        "with_planning": True,
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

        if self.options.with_gui and not self.options.with_utils:
            raise ConanInvalidConfiguration("Option 'with_gui' requires option 'with_utils'")

        if self.options.with_gui_osg and not self.options.with_gui:
            raise ConanInvalidConfiguration("Option 'with_gui_osg' requires option 'with_gui'")

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

        # FIXME: Casing
        tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "Findflann.cmake"),
                        "pkg_check_modules(PC_FLANN flann QUIET)",
                        'pkg_check_modules(PC_FLANN flann_cpp)\nmessage(">>>>>> PC_FLANN_LIBDIR: ${PC_FLANN_LIBDIR}")\nmessage(">>>>>> PC_FLANN_VERSION: ${PC_FLANN_VERSION}")')
        tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "Findflann.cmake"),
                        "find_library(FLANN_LIBRARIES flann_cpp",
                        'find_library(FLANN_LIBRARIES flann_cpp_s')
        tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "Findlz4.cmake"),
                        "pkg_check_modules(PC_lz4 lz4 QUIET)",
                        'pkg_check_modules(PC_lz4 liblz4)\nmessage(">>>>>> PC_lz4_INCLUDEDIR: ${PC_lz4_INCLUDEDIR}")')
        #tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "DARTFindflann.cmake"),
        #                "find_package(flann 1.8.4 QUIET MODULE)",
        #                "find_package(Flann 1.8.4 MODULE)")
        #tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "DARTFindflann.cmake"),
        #                "if((FLANN_FOUND OR flann_FOUND) AND NOT TARGET flann)",
        #                "if((Flann_FOUND OR flann_FOUND) AND NOT TARGET Flann)")

        #tools.replace_in_file(os.path.join(self._source_subfolder, "dart", "planning", "CMakeLists.txt"),
        #                "target_link_libraries(${target_name} PUBLIC dart flann lz4)",
        #                "target_link_libraries(${target_name} PUBLIC dart Flann::Flann)")
        #tools.replace_in_file(os.path.join(self._source_subfolder, "dart", "planning", "CMakeLists.txt"),
        #                'dart_check_optional_package(FLANN "dart-planning" "flann" "1.8.4")',
        #                '# dart_check_optional_package(Flann "dart-planning" "flann" "1.8.4")')
                        

    def requirements(self):
        self.requires("eigen/3.4.0")
        self.requires("libccd/2.1")
        self.requires("fcl/0.6.1")
        self.requires("assimp/5.0.1")
        self.requires("boost/1.76.0")
        self.requires("octomap/1.9.7")
        if self.options.with_utils:
            self.requires("tinyxml2/8.0.0")
        if self.options.with_gui:
            self.requires("opengl/system")
            self.requires("freeglut/3.2.1")
        if self.options.with_gui_osg:
            self.requires("openscenegraph/3.6.5")
        if self.options.with_optimizer_nlopt:
            self.requires("nlopt/2.7.0")
        if self.options.with_optimizer_pagmo:
            self.requires("pagmo2/2.17.0")
        if self.options.with_collision_bullet:
            self.requires("bullet3/3.17")
        if self.options.with_planning:
            self.requires("flann/1.9.1")
        #if self.options.with_imgui:
        #    self.requires("imgui/1.83")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        #self._cmake.definitions["CMAKE_VERBOSE_MAKEFILE"] = True
        self._cmake.definitions["DART_VERBOSE"] = True
        self._cmake.definitions["EIGEN3_VERSION_STRING"] = self.deps_cpp_info["eigen"].version
        self._cmake.definitions["HAS_BOOST_ALGORITHM_LEXICAL_CAST"] = True  # This check doesn't work with the multi generator
        self._cmake.definitions["DART_BUILD_GUI_OSG"] = self.options.with_gui_osg
        self._cmake.definitions["DART_BUILD_DARTPY"] = False
        self._cmake.definitions["DART_BUILD_EXTRAS"] = False
        self._cmake.definitions["DART_BUILD_DARTPY"] = False
        self._cmake.definitions["DART_SKIP_DOXYGEN"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        os.remove("flann-config.cmake")

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

        if self.options.with_gui:
            self.cpp_info.components["gui"].libs = ["dart-gui"]
            self.cpp_info.components["gui"].requires = ["utils", "opengl::opengl", "freeglut::freeglut",
                                                        "external-lodepng", "external-imgui"]

        if self.options.with_gui_osg:
            self.cpp_info.components["gui-osg"].libs = ["dart-gui-osg"]
            self.cpp_info.components["gui-osg"].requires = ["gui", "openscenegraph::openscenegraph"]

        if self.options.with_optimizer_nlopt:
            self.cpp_info.components["optimizer-nlopt"].libs = ["dart-optimizer-nlopt"]
            self.cpp_info.components["optimizer-nlopt"].requires = ["core", "nlopt::nlopt"]

        if self.options.with_gui_osg:
            self.cpp_info.components["optimizer-pagmo"].libs = ["dart-optimizer-pagmo"]
            self.cpp_info.components["optimizer-pagmo"].requires = ["core", "pagmo::pagmo", 
                                                                    "boost::serialization"]

        if self.options.with_collision_bullet:
            self.cpp_info.components["collision-bullet"].libs = ["dart-collision-bullet"]
            self.cpp_info.components["collision-bullet"].requires = ["core", "bullet3::bullet3"]

        if self.options.with_planning:
            self.cpp_info.components["planning"].libs = ["dart-planning"]
            self.cpp_info.components["planning"].requires = ["core", "flann::flann"]
