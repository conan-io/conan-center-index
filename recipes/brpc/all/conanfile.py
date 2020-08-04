from conans import CMake, ConanFile, tools
import glob
import os


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
        "with_snappy": [True, False],
        "with_glog": [True, False],
        "with_thrift": [True, False],
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "with_snappy": True,
        "with_glog": True,
        "with_thrift": False,
        "shared": False,
        "fPIC": True,
    }

    _cmake = None

    def requirements(self):
        self.requires("gflags/2.2.2")
        self.requires("protobuf/3.9.1")
        self.requires("leveldb/1.22")
        self.requires("openssl/1.1.1g")
        self.requires("zlib/1.2.11")
        if self.options.with_glog:
            self.requires("glog/0.4.0")
        if self.options.with_thrift:
            self.requires("thrift/0.13.0")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        self.options['protobuf'].with_zlib = True
        self.options['leveldb'].with_snappy = self.options.with_snappy
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("incubator-brpc-" + self.version, self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["WITH_GLOG"] = self.options.with_glog
        self._cmake.definitions["WITH_THRIFT"] = self.options.with_thrift
        if self.options.with_snappy:
            self._cmake.definitions["WITH_SNAPPY"] = True
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def _remove_files(self, path, patterns):
        for file_pattern in patterns:
            for file in glob.glob(os.path.join(path, file_pattern)):
                os.remove(file)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        lib_path = os.path.join(self.package_folder, "lib")
        if self.options.shared:
            self._remove_files(lib_path, ["*.a", "*.lib"])
        else:
            self._remove_files(lib_path, ["*.so", "*.dylib", "*.dll"])
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            if self.settings.os == "Linux":
                self.cpp_info.system_libs = ["pthread"]
