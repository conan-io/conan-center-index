import os
import conan.tools.files
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.36.0"


class IgnitionPluginConan(ConanFile):
    name = "ignition-plugin"
    license = "Apache-2.0"
    homepage = "https://github.com/ignitionrobotics/ign-plugin"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Protobuf messages and functions for robot applications..."
    topics = ("ignition", "robotics", "plugin")
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

    def validate(self):
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            raise ConanInvalidConfiguration("sorry, M1 builds are not currently supported, give up!")
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
        elif tools.Version(self.settings.compiler.version) < min_version:
            raise ConanInvalidConfiguration(
                "{} requires c++17 support. The current compiler {} {} does not support it.".format(
                    self.name,
                    self.settings.compiler,
                    self.settings.compiler.version,
                )
            )
    
    def requirements(self):
        pass

    def build_requirements(self):
        self.build_requires("doxygen/1.9.2")
        if self.version <= "1.2.0":
            self.build_requires("ignition-cmake/2.5.0")
        else:
            self.build_requires("ignition-cmake/2.10.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        conan.tools.files.rename(
             self, "ign-plugin-ignition-plugin_{}".format(self.version),
             self._source_subfolder
            )

    def _configure_cmake(self):
        if self._cmake is not None:
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
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "bin"))
        

        # Remove MS runtime files
        for dll_pattern_to_remove in ["concrt*.dll", "msvcp*.dll", "vcruntime*.dll"]:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), dll_pattern_to_remove)

    def package_info(self):
        version_major = tools.Version(self.version).major
        self.cpp_info.names["cmake_find_package"] = "ignition-plugin{}".format(version_major)
        self.cpp_info.names["cmake_find_package_multi"] = "ignition-plugin{}".format(version_major)
        self.cpp_info.components["core"].libs = ["ignition-plugin{}".format(version_major)]
        self.cpp_info.components["core"].includedirs.append("include/ignition/plugin{}".format(version_major))
        self.cpp_info.components["core"].names["cmake_find_package"] = "ignition-plugin{}".format(version_major)
        self.cpp_info.components["core"].names["cmake_find_package_multi"] = "ignition-plugin{}".format(version_major)
        self.cpp_info.components["core"].names["pkg_config"] = "ignition-plugin{}".format(version_major)

        self.cpp_info.components["loader"].names["cmake_find_package"] = "ignition-plugin{}-loader".format(version_major)
        self.cpp_info.components["loader"].names["cmake_find_package_multi"] = "ignition-plugin{}-loader".format(version_major)
        self.cpp_info.components["loader"].names["pkg_config"] = "ignition-plugin{}-loader".format(version_major)
        self.cpp_info.components["loader"].libs = ["ignition-plugin{}-loader".format(version_major)]
        self.cpp_info.components["loader"].includedirs = ["include/ignition/plugin{}".format(version_major)]

        if self.options.shared:
            self.cpp_info.components["register"].names["cmake_find_package"] = "ignition-plugin{}-register".format(version_major)
            self.cpp_info.components["register"].names["cmake_find_package_multi"] = "ignition-plugin{}-register".format(version_major)
            self.cpp_info.components["register"].names["pkg_config"] = "ignition-plugin{}-register".format(version_major)
            self.cpp_info.components["register"].includedirs = ["include/ignition/plugin{}".format(version_major)]

