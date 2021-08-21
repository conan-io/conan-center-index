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
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        #"with_imgui": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
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

    def validate(self):
        # TODO: Check for C++14 (double-check)
        pass

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

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
        #if self.options.with_imgui:
        #    self.requires("imgui/1.83")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["DART_VERBOSE"] = True
        self._cmake.definitions["EIGEN3_VERSION_STRING"] = self.deps_cpp_info["eigen"].version
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        # tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        # Steal component name 'dart'
        self.cpp_info.components["dart-core"].names["cmake_find_package"] = "dart"
        self.cpp_info.components["dart-core"].names["cmake_find_package_multi"] = "dart"
        self.cpp_info.components["dart-core"].libs = ["dart"]
        self.cpp_info.components["dart-core"].requires = ["eigen::eigen", "libccd::libccd", "fcl::fcl",
                                                          "assimp::assimp", "boost::boost", "octomap::octomap"]

        self.cpp_info.components["dart-external-imgui"].libs = ["dart-external-imgui"]
        self.cpp_info.components["dart-external-lodepng"].libs = ["dart-external-lodepng"]
        self.cpp_info.components["dart-external-odelcpsolver"].libs = ["dart-external-odelcpsolver"]
