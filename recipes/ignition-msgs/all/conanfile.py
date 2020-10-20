import os

from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class IgnitionMsgsConan(ConanFile):
    name = "ignition-msgs"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://ignitionrobotics.org/libs/msgs"
    description = "Ignition Messages is a component in the ignition framework, a set of libraries designed to rapidly develop robot applications."
    topics = ("ignition", "msgs", "robotics", "gazebo")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake", "cmake_find_package_multi", "pkg_config"
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

    @property
    def _cmake_source_subfolder(self):
        return "cmake_source_subfolder"

    @property
    def _cmake_build_subfolder(self):
        return "cmake_build_subfolder"

    @property
    def _cmake_prefix_subfolder(self):
        return "cmake_prefix_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        version_major = self.version.split(".")[0]
        os.rename(
            "ign-msgs-ignition-msgs{}_{}".format(version_major, self.version),
            self._source_subfolder,
        )

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
        self.requires("tinyxml2/8.0.0")
        self.requires("protobuf/3.12.3")
        self.requires("ignition-msgs/6.6.0")

    def build_requirements(self):
        self.build_requires("pkgconf/1.7.3")
        self.build_requires("ignition-cmake/2.5.0")

    def _configure_cmake(self):
        if self._cmake is not None:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.verbose = True
        self._cmake.definitions["BUILD_TESTING"] = False
        # self._cmake.definitions["CMAKE_PREFIX_PATH"] = os.path.join(self.build_folder, self._cmake_prefix_subfolder)
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
        self.cpp_info.names["cmake_find_package"] = "ignition-msgs{}".format(version_major)
        self.cpp_info.names["cmake_find_package_multi"] = "ignition-msgs{}".format(version_major)

        # FIXME: create in file ignition-msgs6-all-config.cmake
        self.cpp_info.components["libignition-msgs-all"].libs = []
        self.cpp_info.components["libignition-msgs-all"].requires = ["libignition-msgs-eigen3"]
        self.cpp_info.components["libignition-msgs-all"].names["cmake_find_package"] = "ignition-msgs{}-all".format(version_major)
        self.cpp_info.components["libignition-msgs-all"].names["cmake_find_package_multi"] = "ignition-msgs{}-all".format(version_major)
