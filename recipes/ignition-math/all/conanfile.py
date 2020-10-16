import glob
import os

from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration


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
    generators = "cmake_find_package_multi"

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

    def configure(self):
        if self.settings.get_safe("compiler.cppstd"):
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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        version_major = self.version.split(".")[0]
        os.rename(
            "ign-math-ignition-math{}_{}".format(version_major, self.version),
            self._source_subfolder,
        )

    def requirements(self):
        self.requires("eigen/3.3.7")

    def _configure_cmake(self):
        if self._cmake is not None:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def build(self):
        self._install_ign_cmake()
        self._configure_cmake()
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
            for dll_to_remove in glob.glob(os.path.join(self.package_folder, "bin", dll_pattern_to_remove)):
                os.remove(dll_to_remove)

    def package_info(self):
        version_major = self.version.split(".")[0]
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.names["cmake_find_package_multi"] = "ignition-math{}".format(
            version_major
        )
        self.cpp_info.includedirs = ["include/ignition/math{}".format(version_major)]

    def _install_ign_cmake(self):
        # Get and build ign-cmake. This is just a set of cmake macros used by all the ignition
        # packages.
        # TODO: find a way of using an ign-make Conan package as a
        # build_requirement
        self.run(
            "git clone --depth=1 https://github.com/ignitionrobotics/ign-cmake.git --branch ignition-cmake2_2.5.0"
        )
        cmake = CMake(self)
        cmake.configure(source_folder="ign-cmake", build_folder="build_ign-cmake")
        cmake.build()
        cmake.install()
