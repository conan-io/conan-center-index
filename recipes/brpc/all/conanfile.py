import os
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version

#FIXME: cleanup imports

class BrpcConan(ConanFile):
    name = "brpc"
    description = "TODO" #FIXME
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

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        self.requires("gflags/2.2.2", "protobuf/3.9.1", "leveldb/1.22")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("incubator-brpc-" + self.version, self._source_subfolder)

    def _patch_sources(self):
        tools.patch(**self.conan_data["main_patches"][self.version])
        if self.options.with_snappy:
            tools.patch(**self.conan_data["snappy_patches"][self.version])

    def build(self):
        self._patch_sources()
        print("build done")
