import os
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import conan.tools.files

required_conan_version = ">=1.29.1"


class IgnitionMsgsConan(ConanFile):
    name = "ignition-msgs"
    license = "Apache-2.0"
    homepage = "https://github.com/ignitionrobotics/ign-msgs"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Protobuf messages and functions for robot applications..."
    topics = ("ignition", "robotics", "msgs")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake", "cmake_find_package"
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
        self.requires("protobuf/3.17.1@")
        self.requires("tinyxml2/8.0.0@")
        if int(tools.Version(self.version).major) == 5:
            ## waiting for ignition-tools to get merged to master in ar-conan-thirdparty
            #self.build_requires("ignition-tools/1.0.0")
            self.requires("ignition-math/6.7.0")
        elif int(tools.Version(self.version).major) == 8:
            ## waiting for ignition-tools to get merged to master in ar-conan-thirdparty
            #self.build_requires("ignition-cmake/1.4.0")
            self.requires("ignition-math/6.9.0")

    def build_requirements(self):
        # at least cmake version 3.15.0 is needed by tinyxml2
        self.build_requires("doxygen/1.8.17@")
        self.build_requires("ignition-cmake/2.10.0")


    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        version_major = tools.Version(self.version).major
        conan.tools.files.rename(
             self, f"ign-msgs-ignition-msgs{version_major}_{self.version}",
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
        version_major = tools.Version(self.version).major
        self.copy("msgs.hh", 
                 dst=os.path.join(self.package_folder,"include","ignition", f"msgs{version_major}"),
                 src=os.path.join(self._source_subfolder, "include", "ignition"))
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
        self.cpp_info.names["cmake_find_package"] = f"ignition-msgs{version_major}"
        self.cpp_info.names["cmake_find_package_multi"] = "ignition-msgs{version_major}"

        self.cpp_info.components["core"].libs = [f"ignition-msgs{version_major}"]
        self.cpp_info.components["core"].includedirs.append(f"include/ignition/msgs{version_major}")
        self.cpp_info.components["core"].names["cmake_find_package"] = f"ignition-msgs{version_major}"
        self.cpp_info.components["core"].names["cmake_find_package_multi"] = f"ignition-msgs{version_major}"
        self.cpp_info.components["core"].names["pkg_config"] = f"ignition-msgs{version_major}"
        self.cpp_info.components["core"].requires = ["ignition-math::ignition-math"]
        self.cpp_info.components["core"].requires.append("protobuf::protobuf")
        self.cpp_info.components["core"].requires.append("tinyxml2::tinyxml2")

