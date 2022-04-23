from conan.tools.microsoft import msvc_runtime_flag
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import glob
import shutil

required_conan_version = ">=1.43.0"


class RocksDB(ConanFile):
    name = "rocksdb"
    homepage = "https://github.com/facebook/rocksdb"
    license = ("GPL-2.0-only", "Apache-2.0")
    url = "https://github.com/conan-io/conan-center-index"
    description = "A library that provides an embeddable, persistent key-value store for fast storage"
    topics = ("rocksdb", "database", "leveldb", "facebook", "key-value")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "lite": [True, False],
        "with_gflags": [True, False],
        "with_snappy": [True, False],
        "with_lz4": [True, False],
        "with_zlib": [True, False],
        "with_zstd": [True, False],
        "with_tbb": [True, False],
        "with_jemalloc": [True, False],
        "enable_sse": [False, "sse42", "avx2"],
        "use_rtti": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "lite": False,
        "with_snappy": False,
        "with_lz4": False,
        "with_zlib": False,
        "with_zstd": False,
        "with_gflags": False,
        "with_tbb": False,
        "with_jemalloc": False,
        "enable_sse": False,
        "use_rtti": False,
    }

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch != "x86_64":
            del self.options.with_tbb
        if self.settings.build_type == "Debug":
            self.options.use_rtti = True  # Rtti are used in asserts for debug mode...

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.with_gflags:
            self.requires("gflags/2.2.2")
        if self.options.with_snappy:
            self.requires("snappy/1.1.9")
        if self.options.with_lz4:
            self.requires("lz4/1.9.3")
        if self.options.with_zlib:
            self.requires("zlib/1.2.12")
        if self.options.with_zstd:
            self.requires("zstd/1.5.2")
        if self.options.get_safe("with_tbb"):
            self.requires("onetbb/2020.3")
        if self.options.with_jemalloc:
            self.requires("jemalloc/5.2.1")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)
        if self.settings.arch not in ["x86_64", "ppc64le", "ppc64", "mips64", "armv8"]:
            raise ConanInvalidConfiguration("Rocksdb requires 64 bits")

        if self.settings.os == "Windows" and \
           self.settings.compiler == "Visual Studio" and \
           tools.Version(self.settings.compiler.version) < "15":
            raise ConanInvalidConfiguration("Rocksdb requires Visual Studio 15 or later.")

        if self.version == "6.0.2" and \
           self.settings.os == "Windows" and \
           self.settings.compiler == "Visual Studio" and \
           tools.Version(self.settings.compiler.version) > "15":
            raise ConanInvalidConfiguration("Rocksdb 6.0.2 is not compilable with Visual Studio >15.") # See https://github.com/facebook/rocksdb/issues/6048

        if self.version == "6.0.2" and \
           self.settings.os == "Linux" and \
           self.settings.compiler == "clang" and \
           tools.Version(self.settings.compiler.version) > "9":
            raise ConanInvalidConfiguration("Rocksdb 6.0.2 is not compilable with clang >9.") # See https://github.com/facebook/rocksdb/pull/7265

        if self.version == "6.20.3" and \
           self.settings.os == "Linux" and \
           self.settings.compiler == "gcc" and \
           tools.Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("Rocksdb 6.20.3 is not compilable with gcc <5.") # See https://github.com/facebook/rocksdb/issues/3522

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)

        self._cmake.definitions["FAIL_ON_WARNINGS"] = False
        self._cmake.definitions["WITH_TESTS"] = False
        self._cmake.definitions["WITH_TOOLS"] = False
        self._cmake.definitions["WITH_CORE_TOOLS"] = False
        self._cmake.definitions["WITH_BENCHMARK_TOOLS"] = False
        self._cmake.definitions["WITH_FOLLY_DISTRIBUTED_MUTEX"] = False
        if self._is_msvc:
            self._cmake.definitions["WITH_MD_LIBRARY"] = "MD" in msvc_runtime_flag(self)
        self._cmake.definitions["ROCKSDB_INSTALL_ON_WINDOWS"] = self.settings.os == "Windows"
        self._cmake.definitions["ROCKSDB_LITE"] = self.options.lite
        self._cmake.definitions["WITH_GFLAGS"] = self.options.with_gflags
        self._cmake.definitions["WITH_SNAPPY"] = self.options.with_snappy
        self._cmake.definitions["WITH_LZ4"] = self.options.with_lz4
        self._cmake.definitions["WITH_ZLIB"] = self.options.with_zlib
        self._cmake.definitions["WITH_ZSTD"] = self.options.with_zstd
        self._cmake.definitions["WITH_TBB"] = self.options.get_safe("with_tbb", False)
        self._cmake.definitions["WITH_JEMALLOC"] = self.options.with_jemalloc
        self._cmake.definitions["ROCKSDB_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["ROCKSDB_LIBRARY_EXPORTS"] = self.settings.os == "Windows" and self.options.shared
        self._cmake.definitions["ROCKSDB_DLL" ] = self.settings.os == "Windows" and self.options.shared

        self._cmake.definitions["USE_RTTI"] = self.options.use_rtti
        if self.options.enable_sse == "False":
          self._cmake.definitions["PORTABLE"] = True
          self._cmake.definitions["FORCE_SSE42"] = False
        elif self.options.enable_sse == "sse42":
          self._cmake.definitions["PORTABLE"] = True
          self._cmake.definitions["FORCE_SSE42"] = True
        elif self.options.enable_sse == "avx2":
          self._cmake.definitions["PORTABLE"] = False
          self._cmake.definitions["FORCE_SSE42"] = False

        # not available yet in CCI

        self._cmake.definitions["WITH_NUMA"] = False

        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            self._cmake.definitions["CMAKE_CXX_FLAGS"] = "-march=armv8-a"

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def _remove_static_libraries(self):
        for static_lib_name in ["lib*.a", "rocksdb.lib"]:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), static_lib_name)

    def _remove_cpp_headers(self):
        for path in glob.glob(os.path.join(self.package_folder, "include", "rocksdb", "*")):
            if path != os.path.join(self.package_folder, "include", "rocksdb", "c.h"):
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    shutil.rmtree(path)

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        self.copy("LICENSE*", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        if self.options.shared:
            self._remove_static_libraries()
            self._remove_cpp_headers() # Force stable ABI for shared libraries
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        cmake_target = "rocksdb-shared" if self.options.shared else "rocksdb"
        self.cpp_info.set_property("cmake_file_name", "RocksDB")
        self.cpp_info.set_property("cmake_target_name", "RocksDB::{}".format(cmake_target))
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["librocksdb"].libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.components["librocksdb"].system_libs = ["shlwapi", "rpcrt4"]
            if self.options.shared:
                self.cpp_info.components["librocksdb"].defines = ["ROCKSDB_DLL"]
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["librocksdb"].system_libs = ["pthread", "m"]
        if self.options.lite:
            self.cpp_info.components["librocksdb"].defines.append("ROCKSDB_LITE")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "RocksDB"
        self.cpp_info.names["cmake_find_package_multi"] = "RocksDB"
        self.cpp_info.components["librocksdb"].names["cmake_find_package"] = cmake_target
        self.cpp_info.components["librocksdb"].names["cmake_find_package_multi"] = cmake_target
        self.cpp_info.components["librocksdb"].set_property("cmake_target_name", "RocksDB::{}".format(cmake_target))
        if self.options.with_gflags:
            self.cpp_info.components["librocksdb"].requires.append("gflags::gflags")
        if self.options.with_snappy:
            self.cpp_info.components["librocksdb"].requires.append("snappy::snappy")
        if self.options.with_lz4:
            self.cpp_info.components["librocksdb"].requires.append("lz4::lz4")
        if self.options.with_zlib:
            self.cpp_info.components["librocksdb"].requires.append("zlib::zlib")
        if self.options.with_zstd:
            self.cpp_info.components["librocksdb"].requires.append("zstd::zstd")
        if self.options.get_safe("with_tbb"):
            self.cpp_info.components["librocksdb"].requires.append("onetbb::onetbb")
        if self.options.with_jemalloc:
            self.cpp_info.components["librocksdb"].requires.append("jemalloc::jemalloc")
