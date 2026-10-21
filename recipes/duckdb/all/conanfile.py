from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, rm, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout

import glob
import os

required_conan_version = ">=2.1"

class DuckdbConan(ConanFile):
    name = "duckdb"
    description = "DuckDB is an embeddable SQL OLAP Database Management System"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cwida/duckdb"
    topics = ("sql", "database", "olap", "embedded-database")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_autocomplete": [True, False],
        "with_icu": [True, False],
        "with_tpch": [True, False],
        "with_tpcds": [True, False],
        "with_fts": [True, False],
        "with_visualizer": [True, False],
        "with_httpfs": [True, False],
        "with_json": [True, False],
        "with_excel": [True, False],
        "with_inet": [True, False],
        "with_sqlsmith": [True, False],
        "with_query_log": [True, False],
        "with_shell": [True, False],
        "with_threads": [True, False],
        "with_rdtsc": [True, False],
        "with_extension_load": [True, False],
        "with_httplib": [True, False],
        "with_jemalloc": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_autocomplete": False,
        "with_icu": False,
        "with_tpch": False,
        "with_tpcds": False,
        "with_fts": False,
        "with_visualizer": False,
        "with_httpfs": False,
        "with_json": False,
        "with_excel": False,
        "with_inet": False,
        "with_sqlsmith": False,
        "with_query_log": False,
        "with_shell": False,
        "with_threads": True,
        "with_rdtsc": False,
        "with_extension_load": True,
        "with_httplib": True,
        "with_jemalloc": True,
    }
    short_paths = True

    @property
    def _min_cppstd(self):
        return 11 if Version(self.version) < "2.0.0" else 17

    def export_sources(self):
        copy(self, "cmake/*", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "1.5.0":
            del self.options.with_httplib
        # From 1.5.0 jemalloc is an allocator switch, used on 64-bit Linux only
        if Version(self.version) < "1.5.0" or self.settings.os != "Linux" or \
                self.settings.arch not in ["x86_64", "armv8"]:
            del self.options.with_jemalloc
        if Version(self.version) >= "1.5.0":
            # Out-of-tree extensions: CMake would git clone them during the build
            for option in ["with_fts", "with_visualizer", "with_httpfs", "with_excel", "with_inet", "with_sqlsmith"]:
                self.options.rm_safe(option)
        if Version(self.version) >= "2.0.0":
            # Statically linked by default since 2.0.0
            self.options.with_json = True
            self.options.with_icu = True

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.get_safe("with_httpfs"):
            self.requires("openssl/[>=1.1 <4]")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        # FIXME: drop support MSVC debug shared build
        if is_msvc(self) and self.options.shared and self.settings.build_type == "Debug":
            raise ConanInvalidConfiguration(f"{self.ref} does not support MSVC debug shared build")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["DUCKDB_MAJOR_VERSION"] = Version(self.version).major
        tc.variables["DUCKDB_MINOR_VERSION"] = Version(self.version).minor
        tc.variables["DUCKDB_PATCH_VERSION"] = Version(self.version).patch
        tc.variables["DUCKDB_DEV_ITERATION"] = 0
        tc.variables["OVERRIDE_GIT_DESCRIBE"] = f"v{self.version}"

        extensions = [name for name in ["icu", "autocomplete", "tpch", "tpcds", "fts", "visualizer", "httpfs",
                                        "json", "excel", "inet", "sqlsmith"]
                      if self.options.get_safe(f"with_{name}")]
        tc.variables["BUILD_EXTENSIONS"] = "".join(f";{name}" for name in extensions)
        if Version(self.version) >= "2.0.0":
            # Extensions are only linked when listed; the list replaces upstream's default
            # (core_functions, parquet, json, icu), so with_json/with_icu=False take effect
            tc.variables["STATICALLY_LINK_EXTENSIONS"] = ";".join(["core_functions", "parquet"] + extensions)
            tc.variables["ENABLE_EXTENSION_LOAD"] = self.options.with_extension_load
            tc.variables["ENABLE_BUILTIN_HTTPLIB"] = self.options.with_httplib
            # Leave out the local_extension_repository capability: it points automatic installs at the build tree
            capabilities = [name for name, enabled in [("httplib", self.options.with_httplib),
                                                       ("loadable_extensions", self.options.with_extension_load)]
                            if enabled]
            tc.variables["DUCKDB_CAPABILITIES"] = ";".join(capabilities) or "none"
        else:
            tc.variables["DISABLE_EXTENSION_LOAD"] = not self.options.with_extension_load
            if Version(self.version) >= "1.5.0":
                tc.variables["DISABLE_BUILTIN_HTTPLIB"] = not self.options.with_httplib
        if Version(self.version) >= "1.5.0":
            tc.variables["ENABLE_JEMALLOC"] = bool(self.options.get_safe("with_jemalloc", False))

        tc.variables["FORCE_QUERY_LOG"] = self.options.with_query_log
        tc.variables["BUILD_SHELL"] = self.options.with_shell
        tc.variables["DISABLE_THREADS"] = not self.options.with_threads
        tc.variables["BUILD_UNITTESTS"] = False
        tc.variables["BUILD_RDTSC"] = self.options.with_rdtsc
        tc.variables["EXTENSION_STATIC_BUILD"] = not self.options.shared
        tc.variables["ENABLE_SANITIZER"] = False
        tc.variables["ENABLE_UBSAN"] = False
        if is_msvc(self) and not self.options.shared:
            tc.preprocessor_definitions["DUCKDB_API"] = ""
        if is_msvc(self) and self.settings.build_type == "Debug" and Version(self.version) >= "2.0.0":
            # Upstream adds -DDEBUG to Debug builds for GCC/Clang only. Without it, MSVC Debug compiles D_ASSERT as
            # assert() while the helpers some asserts call only exist when DEBUG defines D_ASSERT_IS_ENABLED; and
            # DEBUG itself does not compile with MSVC (src/common/symbols.cpp). Disable assert() as in release builds;
            # the debug runtime and iterator debugging depend on _DEBUG, not NDEBUG
            tc.preprocessor_definitions["NDEBUG"] = "1"
        if cross_building(self):
            tc.variables["DUCKDB_EXPLICIT_PLATFORM"] = f"{self.settings.os}_{self.settings.arch}"
        # INFO: third_party/re2/CMakeLists.txt:32 (CMake version 3.4)
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"
        if is_msvc(self):
            # INFO: Need for MSVC to set correct __cplusplus value
            # Otherwise, fails with: error C2039: 'uncaught_exception': is not a member of 'std' (dropped in C++20)
            # https://github.com/duckdb/duckdb/issues/2805#issuecomment-1013889896
            tc.extra_cxxflags.append("/Zc:__cplusplus")
        tc.generate()

        dpes = CMakeDeps(self)
        dpes.generate()

    def build(self):
        if Version(self.version) >= "1.5.0":
            # Upstream forces the static MSVC runtime; let the profile's compiler.runtime decide
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            'set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")',
                            "")
        if Version(self.version) >= "2.0.0" and not self.options.shared:
            loader = os.path.join(self.export_sources_folder, "cmake", "conan_static_extension_loader.cmake")
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            "duckdb_link_deferred_extension_libraries()",
                            "duckdb_link_deferred_extension_libraries()\n"
                            f"include(\"{loader.replace(os.sep, '/')}\")")
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

        if self.options.shared:
            rm(self, "duckdb_*.lib", os.path.join(self.package_folder, "lib"))
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

    def _static_libs_2_0(self):
        # The loader references the extensions and capabilities, which depend on duckdb_static
        libs = ["duckdb_static_extension_loader"]
        if self.options.with_autocomplete:
            libs.append("autocomplete_extension")
        if self.options.with_tpch:
            libs.append("tpch_extension")
        if self.options.with_tpcds:
            libs.append("tpcds_extension")
        if self.options.with_json:
            libs.append("json_extension")
        if self.options.with_icu:
            libs.append("icu_extension")
        libs += ["core_functions_extension", "parquet_extension"]
        if self.options.with_httplib:
            libs.append("duckdb_httplib")
        if self.options.with_extension_load:
            libs.append("duckdb_loadable_extensions")
        libs.append("duckdb_static")
        libs += ["duckdb_fmt", "duckdb_re2", "duckdb_miniz", "duckdb_utf8proc", "duckdb_hyperloglog",
                 "duckdb_fastpforlib", "duckdb_mbedtls", "duckdb_fsst", "duckdb_zstd",
                 "duckdb_skiplistlib", "duckdb_yyjson"]
        if self.options.get_safe("with_jemalloc"):
            libs.append("duckdb_jemalloc")
        return libs

    def package_info(self):
        if self.options.shared:
            self.cpp_info.libs = ["duckdb"]
        elif Version(self.version) >= "2.0.0":
            self.cpp_info.libs = self._static_libs_2_0()
            # Nothing references the extension registration in duckdb_static_extension_loader (it runs from a static
            # initializer), so force-link it, or the statically linked extensions are never registered
            anchor = "duckdb_static_extension_loader_anchor"
            if is_msvc(self):
                flag = f"/INCLUDE:{'_' if self.settings.arch == 'x86' else ''}{anchor}"
            elif is_apple_os(self):
                flag = f"-Wl,-u,_{anchor}"
            else:
                flag = f"-Wl,-u,{anchor}"
            self.cpp_info.exelinkflags.append(flag)
            self.cpp_info.sharedlinkflags.append(flag)
        else:
            self.cpp_info.libs = [
                "duckdb_static",
                "duckdb_fmt",
                "duckdb_pg_query",
                "duckdb_re2",
                "duckdb_miniz",
                "duckdb_utf8proc",
                "duckdb_hyperloglog",
                "duckdb_fastpforlib",
                "duckdb_mbedtls",
            ]
            if Version(self.version) >= "1.5.0":
                # ExtensionHelper::LoadAllExtensions, called from duckdb_static
                self.cpp_info.libs.insert(1, "duckdb_generated_extension_loader")
            self.cpp_info.libs.append("duckdb_fsst")
            self.cpp_info.libs.append("core_functions_extension")
            self.cpp_info.libs.append("duckdb_zstd")
            self.cpp_info.libs.append("duckdb_skiplistlib")
            self.cpp_info.libs.append("duckdb_yyjson")

            if self.options.with_autocomplete:
                self.cpp_info.libs.append("autocomplete_extension")
            if self.options.with_icu:
                self.cpp_info.libs.append("icu_extension")
            if self.options.get_safe("with_parquet", True):
                self.cpp_info.libs.append("parquet_extension")
            if self.options.with_tpch:
                self.cpp_info.libs.append("tpch_extension")
            if self.options.with_tpcds:
                self.cpp_info.libs.append("tpcds_extension")
            if self.options.get_safe("with_fts"):
                self.cpp_info.libs.append("fts_extension")
            if self.options.get_safe("with_visualizer"):
                self.cpp_info.libs.append("visualizer_extension")
            if self.options.get_safe("with_httpfs"):
                self.cpp_info.libs.append("httpfs_extension")
            if Version(self.version) < "1.5.0":
                if self.settings.os == "Linux" and self.settings.arch == "x86_64":
                    self.cpp_info.libs.append("jemalloc_extension")
            elif self.options.get_safe("with_jemalloc"):
                self.cpp_info.libs.append("duckdb_jemalloc")
            if self.options.with_json:
                self.cpp_info.libs.append("json_extension")
            if self.options.get_safe("with_excel"):
                self.cpp_info.libs.append("excel_extension")
            if self.options.get_safe("with_inet"):
                self.cpp_info.libs.append("inet_extension")
            if self.options.get_safe("with_sqlsmith"):
                self.cpp_info.libs.append("sqlsmith_extension")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "dl", "m"])

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")
            self.cpp_info.system_libs.extend(["rstrtmgr", "bcrypt"])
