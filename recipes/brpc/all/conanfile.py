import os
from conans import CMake, ConanFile, tools

class BrpcConan(ConanFile):
    name = "brpc"
    description = "An industrial-grade RPC framework used throughout Baidu"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/apache/incubator-brpc"
    topics = ("conan", "brpc", "baidu", "rpc")
    license = ("Apache-2.0")
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package"
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
        self.options['protobuf'].with_zlib = True
        self.options['leveldb'].with_snappy = self.options.with_snappy
        # FIXME: add options for with_glog and with_thrift
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
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BRPC_REVISION"] = self.conan_data["git_hashes"][self.version]
        self._cmake.configure()
        return self._cmake


    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # FIXME: brpc builds both static/shared lib and installation currently
        # copies both files
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            if self.settings.os == "Linux":
                self.cpp_info.system_libs = ["pthread"]
