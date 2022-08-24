from from conan import ConanFile, tools
from conans import CMake
import functools
import os

required_conan_version = ">=1.43.0"


class LevelDBCppConan(ConanFile):
    name = "leveldb"
    description = (
        "LevelDB is a fast key-value storage library written at Google that "
        "provides an ordered mapping from string keys to string values."
    )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/leveldb"
    topics = ("leveldb", "google", "db")
    license = ("BSD-3-Clause",)

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

    generators = "cmake", "cmake_find_package_multi"

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

    # FIXME: tcmalloc is also conditionally included in leveldb, but
    # there is no "official" conan package yet; when that is available, we
    # can add similar with options for those

    def requirements(self):
        if self.options.with_snappy:
            self.requires("snappy/1.1.9")
        if self.options.with_crc32c:
            self.requires("crc32c/1.1.2")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["LEVELDB_BUILD_TESTS"] = False
        cmake.definitions["LEVELDB_BUILD_BENCHMARKS"] = False
        cmake.definitions["HAVE_SNAPPY"] = self.options.with_snappy
        cmake.definitions["HAVE_CRC32C"] = self.options.with_crc32c
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "leveldb")
        self.cpp_info.set_property("cmake_target_name", "leveldb::leveldb")
        self.cpp_info.libs = ["leveldb"]
        if self.options.shared:
            self.cpp_info.defines.append("LEVELDB_SHARED_LIBRARY")
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
