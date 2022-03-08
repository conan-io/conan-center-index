import os
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import conan.tools.files

required_conan_version = ">=1.29.1"


class IgnitionUitlsConan(ConanFile):
    name = "ignition-tools"
    license = "Apache-2.0"
    homepage = "https://ignitionrobotics.org/libs/tools"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Provides general purpose classes and functions designed for robotic applications.."
    topics = ("ignition", "robotics", "tools")
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

    #def requirements(self):
    #    self.requires("cli11/2.1.2")

    #def build_requirements(self):
    #    self.build_requires("ignition-cmake/2.5.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        version_major = self.version.split(".")[0]
        os.rename(
             "ign-tools-ignition-tools_{}.{}.{}".format(version_major, "0", "0"),
             self._source_subfolder
            )

    def _configure_cmake(self):
        if self._cmake is not None:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False
        #self._cmake.definitions["IGN_UTILS_VENDOR_CLI11"] = True
        self._cmake.definitions["CMAKE_FIND_DEBUG_MODE"] = "1"
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cli_header_src = os.path.join(self._source_subfolder, "cli", "include")
        #if int(tools.Version(self.version).minor) is 0:
        #    cli_header_src = os.path.join(cli_header_src, "ignition", "tools", "cli")
        #else:
        #    cli_header_src = os.path.join(cli_header_src, "external-cli", "ignition", "tools", "cli")
        #self.copy("*.hpp", src=cli_header_src,
        #             dst="include/ignition/utils1/ignition/tools/cli")
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
        self.cpp_info.names["cmake_find_package"] = "ignition-tools{}".format(version_major)
        self.cpp_info.names["cmake_find_package_multi"] = "ignition-tools{}".format(version_major)

        # cmake_find_package filename: ignition-tools-config.cmake
        self.cpp_info.components["libignition-tools"].libs = ["ignition-tools{}".format(version_major)]
        self.cpp_info.components["libignition-tools"].includedirs.append("include/ignition/tools{}".format(version_major))
        self.cpp_info.components["libignition-tools"].names["cmake_find_package"] = "ignition-tools{}".format(version_major)
        self.cpp_info.components["libignition-tools"].names["cmake_find_package_multi"] = "ignition-tools{}".format(version_major)
        self.cpp_info.components["libignition-tools"].names["pkg_config"] = "ignition-tools{}".format(version_major)
        #self.cpp_info.components["libignition-tools"].requires = ["cli11::cli11"]
        self.env_info.LD_LIBRARY_PATH.extend([
            os.path.join(self.package_folder, x) for x in self.cpp_info.libdirs
        ])
        self.env_info.PATH.extend([
            os.path.join(self.package_folder, x) for x in self.cpp_info.bindirs
        ])