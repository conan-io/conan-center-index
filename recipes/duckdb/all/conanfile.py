from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"

class DuckdbConan(ConanFile):
    name = "duckdb"
    license = "MIT"
    homepage = "https://github.com/cwida/duckdb"
    url = "https://github.com/conan-io/conan-center-index/"
    description = "DuckDB is an embeddable SQL OLAP Database Management System"
    topics = ("sql", "database", "olap", "embedded-database")
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_icu": [True, False],
        "with_parquet": [True, False],
        "with_tpch": [True, False],
        "with_tpcds": [True, False],
        "with_fts": [True, False],
        "with_httpfs": [True, False],
        "with_threads": [True, False],
        "with_rdtsc": [True, False],
        "query_log": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_icu": False,
        "with_parquet": False,
        "with_tpch": False,
        "with_tpcds": False,
        "with_fts": False,
        "with_httpfs": False,
        "query_log": False,
        "with_threads": True,
        "with_rdtsc": False,
    }

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

    def source(self):
        tools.get(**(self.conan_data["sources"][self.version][0]),
                  destination=self._source_subfolder, strip_root=True)
        tools.get(**(self.conan_data["sources"][self.version][1]),
                  destination=os.path.join(self._source_subfolder, "src", "amalgamation"))

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["AMALGAMATION_BUILD"] = True
        self._cmake.definitions["BUILD_UNITTESTS"] = False
        self._cmake.definitions["BUILD_STATIC_LIBS"] = not self.options.shared
        self._cmake.definitions["BUILD_ICU_EXTENSION"] = self.options.with_icu
        self._cmake.definitions["BUILD_PARQUET_EXTENSION"] = self.options.with_parquet
        self._cmake.definitions["BUILD_TPCH_EXTENSION"] = self.options.with_tpch
        self._cmake.definitions["BUILD_TPCDS_EXTENSION"] = self.options.with_tpcds
        self._cmake.definitions["BUILD_FTS_EXTENSION"] = self.options.with_fts
        self._cmake.definitions["BUILD_HTTPFS_EXTENSION"] = self.options.with_httpfs
        self._cmake.definitions["FORCE_QUERY_LOG"] = self.options.query_log
        self._cmake.definitions["DISABLE_THREADS"] = not self.options.with_threads
        self._cmake.definitions["BUILD_RDTSC"] = self.options.with_rdtsc
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        if self.options.shared:
            self.cpp_info.libs = ["duckdb"]  
        else:
            self.cpp_info.libs = ["duckdb_static"]
            if self.options.with_icu:
                self.cpp_info.libs.append("icu_extension")
            if self.options.with_parquet:
                self.cpp_info.libs.append("parquet_extension")
            if self.options.with_tpch:
                self.cpp_info.libs.append("tpch_extension")
            if self.options.with_tpcds:
                self.cpp_info.libs.append("tpcds_extension")
            if self.options.with_fts:
                self.cpp_info.libs.append("fts_extension")
            if self.options.with_httpfs:
                self.cpp_info.libs.append("httpfs_extension")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "dl"]
