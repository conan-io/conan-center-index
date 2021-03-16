import os
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version


class LevelDBCppConan(ConanFile):
    name = "leveldb"
    description = "LevelDB is a fast key-value storage library written at Google that provides an ordered mapping from string keys to string values."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/leveldb"
    topics = ("conan", "leveldb", "google", "db")
    license = ("BSD-3-Clause",)
    exports_sources = ["CMakeLists.txt"]
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

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    # FIXME: crc32, tcmalloc are also conditionally included in leveldb, but
    # there are no "official" conan packages yet; when those are available, we
    # can add similar with options for those
    
    def requirements(self):
        if self.options.with_snappy:
            self.requires("snappy/1.1.8")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["LEVELDB_BUILD_TESTS"] = False
        self._cmake.definitions["LEVELDB_BUILD_BENCHMARKS"] = False
        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        if not self.options.with_snappy:
            tools.replace_in_file(
                    os.path.join(self._source_subfolder, "CMakeLists.txt"),
                    ('''check_library_exists(snappy snappy_compress '''
                        '''"" HAVE_SNAPPY)'''), "")

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
