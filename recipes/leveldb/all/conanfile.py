import os
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version


class LevelDBCppConan(ConanFile):
    name = "leveldb"
    description = "LevelDB is a fast key-value storage library written at Google that provides an ordered mapping from string keys to string values."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/leveldb"
    topics = ("leveldb", "google", "db")
    license = ("BSD-3-Clause",)
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_snappy": [True, False],
        "with_crc32c": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_snappy": True,
        "with_crc32c": True,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    # FIXME: tcmalloc is also conditionally included in leveldb, but
    # there is no "official" conan package yet; when that is available, we
    # can add similar with options for those

    def requirements(self):
        if self.options.with_snappy:
            self.requires("snappy/1.1.8")
        if self.options.with_crc32c:
            self.requires("crc32c/1.1.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["LEVELDB_BUILD_TESTS"] = False
        self._cmake.definitions["LEVELDB_BUILD_BENCHMARKS"] = False
        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            if self.settings.os == "Linux":
                self.cpp_info.system_libs = ["pthread"]
