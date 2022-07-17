from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.43.0"


class CycloneDDSConan(ConanFile):
    name = "cyclone-dds"
    license = "EPL-2.0"
    homepage = "https://cyclonedds.io/"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Eclipse Cyclone DDS - An implementation of the OMG Data Distribution Service (DDS) specification "
    topics = ("DDS", "IPC", "ROS", "Middleware")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "ssl": [True, False],
        "shm" : [True, False],
        "bison" : [True, False]
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "ssl": True,
        "shm": True,
        "bison": False
    }

    generators = ["cmake", "cmake_find_package_multi"]
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])
        
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.shm:
            self.requires("iceoryx/2.0.0")
        if self.options.ssl: 
            self.requires("openssl/1.1.1q")
        if self.options.bison:
            raise ConanInvalidConfiguration("option 'bison' not implemented yet.")

    def validate(self):
        compiler = self.settings.compiler
        version = tools.Version(self.settings.compiler.version)

        if not self.options.shared:
            # see https://github.com/eclipse-cyclonedds/cyclonedds/issues/317
            raise ConanInvalidConfiguration("Currently Cyclone DDS cannot be build statically...")
        if compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 14)

        if compiler == "Visual Studio":
            if version < "16":
                raise ConanInvalidConfiguration("Iceoryx is just supported for Visual Studio 2019 and higher.")
            if self.options.shared:
                raise ConanInvalidConfiguration(
                    'Using Iceoryx with Visual Studio currently just possible with "shared=False"')
        elif compiler == "gcc":
            if version < "6":
                raise ConanInvalidConfiguration("Using Iceoryx with gcc requires gcc 6 or higher.")
            if version < "9" and compiler.get_safe("libcxx") == "libstdc++":
                raise ConanInvalidConfiguration("gcc < 9 with libstdc++ not supported")
            if version == "6":
                self.output.warn("Iceoryx package is compiled with gcc 6, it is recommended to use 7 or higher")
                self.output.warn("GCC 6 will build with warnings.")
        elif compiler == "clang":
            if compiler.get_safe("libcxx") == "libstdc++":
                raise ConanInvalidConfiguration("clang with libstdc++ not supported")
            if version == "7.0" and compiler.get_safe("libcxx") == "libc++" and \
               self.options.shared and self.settings.build_type == "Debug":
                raise ConanInvalidConfiguration("shared Debug with clang 7.0 and libc++ not supported")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_SSL"] = self.options.ssl
        self._cmake.definitions["ENABLE_SHM"] = self.options.shm       
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        
    def package_info(self):
        pass 