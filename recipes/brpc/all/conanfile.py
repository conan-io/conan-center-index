import os
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version

#FIXME: cleanup imports

class BrpcConan(ConanFile):
    name = "brpc"
    description = "" #FIXME
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "" #FIXME
    topics = ("conan", "brpc", "baidu", "rpc")
    license = ("") #FIXME
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_paths", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False], 
        "with_snappy": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_snappy": True,
    }
    requires = "gflags/2.2.2", "protobuf/3.9.1", "leveldb/1.22"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("incubator-brpc-" + self.version, self._source_subfolder)

    def _patch_sources(self):
        tools.patch(**self.conan_data["main_patches"][self.version])
        if self.options.with_snappy:
            tools.patch(**self.conan_data["snappy_patches"][self.version])

    def _configure_cmake(self):
        if self._cmake:
            return self.cmake
        self._cmake = CMake(self)
        #self._cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = "conan_paths.cmake"
        self._cmake.definitions["BRPC_REVISION"] = self.conan_data["git_hashes"][self.version]
        self._cmake.configure()
        return self._cmake


    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()

