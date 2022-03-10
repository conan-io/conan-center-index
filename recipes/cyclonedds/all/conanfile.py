import os
from conans import ConanFile, tools, CMake


class CycloneDDSConan(ConanFile):

    name = "cyclonedds"
    license = "Eclipse Public License - v 2.0"
    author = 'Eclipse Cyclone DDS Contributors'
    description = "Eclipse Cyclone DDS project"
    url = 'https://github.com/eclipse-cyclonedds/cyclonedds'

    options = {
        "enable_ssl": [True, False],
        "enable_security": [True, False],
        "enable_lifespan": [True, False],
        "enable_deadline_missed": [True, False],
        "enable_type_discovery": [True, False],
        "shared": [False, True]
    }
    default_options = {
        "enable_ssl": False,
        "enable_security": True,
        "enable_lifespan": True,
        "enable_deadline_missed": True,
        "enable_type_discovery": True,
        "shared": True
    }

    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ("patches/**", )

    build_requires = "bison/3.7.1"
    generators = "cmake"

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

    def requirements(self):
        if self.options.enable_ssl:
            self.requires("openssl/1.1.1c")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        downloaded_folder_name = "{}-{}".format(self.name, self.version)
        os.rename(downloaded_folder_name, self._source_subfolder)

        return

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        # # set_cmake_flags is necessary to cross-build from 64bit to 32bit on linux
        # cmake = CMake(self, set_cmake_flags=True, append_vcvars=True)
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_SSL"] = self.options.enable_ssl
        self._cmake.definitions[
            "ENABLE_SECURITY"] = self.options.enable_security
        self._cmake.definitions[
            "ENABLE_LIFESPAN"] = self.options.enable_lifespan
        self._cmake.definitions[
            "ENABLE_DEADLINE_MISSED"] = self.options.enable_deadline_missed
        self._cmake.definitions[
            "ENABLE_TYPE_DISCOVERY"] = self.options.enable_type_discovery
        self._cmake.definitions["BUILD_IDLC"] = True

        # # Workaround for an annoying behavior of the vcvarsall and the helper in Conan
        # # vcvarsall also adds CMake and Ninja to the path but by default at the end. The
        # # Conan helper detects which directories were added (but not whether they were added at the beginning or the end)
        # # To prevent CMake version 3.12 from VS 2017 being found we use `append_vcvars=True`. However this causes CMake
        # # to find clang instead of msvc. To force discovery of msvc we explicitly set CMAKE_<LANG>_COMPILER
        # if self._is_windows_os_and_msvc_compiler():
        #     cmake.definitions["CMAKE_C_COMPILER"] = "cl"
        #     cmake.definitions["CMAKE_CXX_COMPILER"] = "cl"

        self._cmake.configure(build_folder=self._build_subfolder,
                              source_folder=self._source_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        assert self.install_folder == self.build_folder, "Build and install folders must be the same"
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.name = "CycloneDDS"
        self.cpp_info.libs = tools.collect_libs(self)

        self.env_info.LD_LIBRARY_PATH.extend([
            os.path.join(self.package_folder, x) for x in self.cpp_info.libdirs
        ])
        self.env_info.PATH.extend([
            os.path.join(self.package_folder, x) for x in self.cpp_info.bindirs
        ])
