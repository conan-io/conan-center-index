import os

from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.29.1"


class IgnitionMathConan(ConanFile):
    name = "ignition-math"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://ignitionrobotics.org/libs/math"
    description = " Math classes and functions for robot applications"
    topics = ("ignition", "math", "robotics", "gazebo")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake", "cmake_find_package_multi"
    exports_sources = "CMakeLists.txt", "patches/**"

    _cmake = None

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "gcc": "7",
            "clang": "5",
            "apple-clang": "10",
        }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn(
                "{} recipe lacks information about the {} compiler support.".format(
                    self.name, self.settings.compiler
                )
            )
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(
                    "{} requires c++17 support. The current compiler {} {} does not support it.".format(
                        self.name,
                        self.settings.compiler,
                        self.settings.compiler.version,
                    )
                )

    def requirements(self):
        self.requires("eigen/3.3.9")

    def build_requirements(self):
        self.build_requires("ignition-cmake/2.5.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        version_major = self.version.split(".")[0]
        os.rename(
            "ign-math-ignition-math{}_{}".format(version_major, self.version),
            self._source_subfolder,
        )

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.configure()
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
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

        # Remove MS runtime files
        for dll_pattern_to_remove in ["concrt*.dll", "msvcp*.dll", "vcruntime*.dll"]:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), dll_pattern_to_remove)

    def package_info(self):
        version_major = tools.Version(self.version).major
        self.cpp_info.names["cmake_find_package"] = "ignition-math{}".format(version_major)
        self.cpp_info.names["cmake_find_package_multi"] = "ignition-math{}".format(version_major)

        # cmake_find_package filename: ignition-math6-config.cmake
        self.cpp_info.components["libignition-math"].libs = ["ignition-math{}".format(version_major)]
        self.cpp_info.components["libignition-math"].includedirs.append("include/ignition/math{}".format(version_major))
        self.cpp_info.components["libignition-math"].names["cmake_find_package"] = "ignition-math{}".format(version_major)
        self.cpp_info.components["libignition-math"].names["cmake_find_package_multi"] = "ignition-math{}".format(version_major)
        self.cpp_info.components["libignition-math"].names["pkg_config"] = "ignition-math{}".format(version_major)

        # FIXME: create in file ignition-math6-eigen3-config.cmake
        self.cpp_info.components["libignition-math-eigen3"].libs = []
        self.cpp_info.components["libignition-math-eigen3"].requires = ["libignition-math", "eigen::eigen"]
        self.cpp_info.components["libignition-math-eigen3"].names["cmake_find_package"] = "ignition-math{}-eigen3".format(version_major)
        self.cpp_info.components["libignition-math-eigen3"].names["cmake_find_package_multi"] = "ignition-math{}-eigen3".format(version_major)
        self.cpp_info.components["libignition-math-eigen3"].names["pkg_config"] = "ignition-math{}-eigen3".format(version_major)

        # FIXME: create in file ignition-math6-all-config.cmake
        self.cpp_info.components["libignition-math-all"].libs = []
        self.cpp_info.components["libignition-math-all"].requires = ["libignition-math-eigen3"]
        self.cpp_info.components["libignition-math-all"].names["cmake_find_package"] = "ignition-math{}-all".format(version_major)
        self.cpp_info.components["libignition-math-all"].names["cmake_find_package_multi"] = "ignition-math{}-all".format(version_major)
