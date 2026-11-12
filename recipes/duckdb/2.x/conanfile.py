from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, rm, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout

import glob
import os

required_conan_version = ">=2.1"

class DuckdbConan(ConanFile):
    name = "duckdb"
    description = "DuckDB is an embeddable SQL OLAP Database Management System"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/duckdb/duckdb"
    topics = ("sql", "database", "olap", "embedded-database")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    short_paths = True

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 17)
        # https://github.com/duckdb/duckdb/issues/27645
        if is_msvc(self) and self.settings.build_type == "Debug":
            raise ConanInvalidConfiguration(f"{self.ref} does not support MSVC Debug builds")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["DUCKDB_MAJOR_VERSION"] = Version(self.version).major
        tc.variables["DUCKDB_MINOR_VERSION"] = Version(self.version).minor
        tc.variables["DUCKDB_PATCH_VERSION"] = Version(self.version).patch
        tc.variables["DUCKDB_DEV_ITERATION"] = 0
        tc.variables["OVERRIDE_GIT_DESCRIBE"] = f"v{self.version}"

        # Upstream's default profile compiles Release builds for a minimum CPU (-march=x86-64-v3, -mcpu=apple-m1)
        tc.variables["DUCKDB_OPTIMIZATION_PROFILE"] = "NONE"
        # Upstream's default also includes local_extension_repository, which points automatic installs at the build tree
        tc.variables["DUCKDB_CAPABILITIES"] = "httplib;loadable_extensions"

        tc.variables["BUILD_SHELL"] = False
        tc.variables["BUILD_UNITTESTS"] = False
        tc.variables["EXTENSION_STATIC_BUILD"] = not self.options.shared
        tc.variables["ENABLE_SANITIZER"] = False
        tc.variables["ENABLE_UBSAN"] = False
        if is_msvc(self) and not self.options.shared:
            tc.preprocessor_definitions["DUCKDB_API"] = ""
        if cross_building(self):
            tc.variables["DUCKDB_EXPLICIT_PLATFORM"] = f"{self.settings.os}_{self.settings.arch}"
        # INFO: third_party/re2/CMakeLists.txt:32 (CMake version 3.4)
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"
        if is_msvc(self):
            # INFO: Need for MSVC to set correct __cplusplus value
            # https://github.com/duckdb/duckdb/issues/2805#issuecomment-1013889896
            tc.extra_cxxflags.append("/Zc:__cplusplus")
        tc.generate()

        dpes = CMakeDeps(self)
        dpes.generate()

    def build(self):
        # Upstream forces the static MSVC runtime, let the profile's compiler.runtime decide
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        'set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")',
                        "")
        if is_msvc(self) and not self.options.shared:
            replace_in_file(self, os.path.join(self.source_folder, "src", "include", "duckdb.h"),
                            f"#define DUCKDB_C_API __declspec(dllimport)",
                            f"#define DUCKDB_C_API"
                            )
            replace_in_file(self, os.path.join(self.source_folder, "src", "include", "duckdb", "common", "winapi.hpp"),
                            f"#define DUCKDB_API __declspec(dllimport)",
                            f"#define DUCKDB_API"
                            )

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        # Upstream installs the C++ API archive for its CMake export set, but not its header
        # (tools/cpp/duckdb_cpp.hpp), so consumers cannot use it
        rm(self, "*duckdb_cpp_api.*", os.path.join(self.package_folder, "lib"))
        if self.options.shared:
            rm(self, "duckdb_*.lib", os.path.join(self.package_folder, "lib"))
            rm(self, "*_extension.lib", os.path.join(self.package_folder, "lib"))
            for lib in glob.glob(os.path.join(self.package_folder, "lib", "*.a")):
                if not lib.endswith(".dll.a"):
                    os.remove(lib)
        else:
            rm(self, "*.dll", os.path.join(self.package_folder, "bin"))
            rm(self, "*.so*", os.path.join(self.package_folder, "lib"))
            rm(self, "*.dylib*", os.path.join(self.package_folder, "lib"))
            rm(self, "duckdb.lib", os.path.join(self.package_folder, "lib"))

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "cmake"))

    def package_info(self):
        if self.options.shared:
            self.cpp_info.libs = ["duckdb"]
        else:
            self.cpp_info.libs = [
                "core_functions_extension",
                "parquet_extension",
                "json_extension",
                "icu_extension",
                "duckdb_httplib",
                "duckdb_loadable_extensions",
                "duckdb_static",
                "duckdb_fmt",
                "duckdb_re2",
                "duckdb_miniz",
                "duckdb_utf8proc",
                "duckdb_hyperloglog",
                "duckdb_fastpforlib",
                "duckdb_mbedtls",
                "duckdb_fsst",
                "duckdb_zstd",
                "duckdb_skiplistlib",
                "duckdb_yyjson",
            ]
            if self.settings.os == "Linux" and self.settings.arch == "x86_64":
                self.cpp_info.libs.append("duckdb_jemalloc")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "dl", "m"])

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")
            self.cpp_info.system_libs.extend(["rstrtmgr", "bcrypt"])
