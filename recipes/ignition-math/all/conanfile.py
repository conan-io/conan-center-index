import os

from conans import CMake, ConanFile, tools


class IgnitionMathConan(ConanFile):
    name = "ignition-math"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://ignitionrobotics.org/libs/math"
    description = " Math classes and functions for robot applications"
    topics = ("ignition", "math", "robotics", "gazebo")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}
    generators = "cmake", "cmake_find_package_multi"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        version_major = self.version[0]
        os.rename(f"ign-math-ignition-math{version_major}_{self.version}", self._source_subfolder)

    def requirements(self):
        self.requires("eigen/3.3.7")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTING"] = False
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def build(self):
        self._install_ign_cmake()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        version_major = self.version[0]
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.names["cmake_find_package"] = f"ignition-math{version_major}"
        self.cpp_info.names["cmake_find_package_multi"] = f"ignition-math{version_major}"
        self.cpp_info.includedirs = [f"include/ignition/math{version_major}"]
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def _install_ign_cmake(self):
        # Get and build ign-cmake. This is just a set of cmake macros used by all the ignition
        # packages.
        # TODO: find a way of using an ign-make Conan package as a
        # build_requirement
        self.run(
            "git clone --depth=1 https://github.com/ignitionrobotics/ign-cmake.git --branch ignition-cmake2_2.5.0")
        cmake = CMake(self)
        cmake.configure(source_folder="ign-cmake",
                        build_folder="build_ign-cmake")
        cmake.build()
        cmake.install()
