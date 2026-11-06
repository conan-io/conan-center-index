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
    homepage = "https://github.com/duckdb/duckdb"
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
        "with_json": [True, False],
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
        # icu and json are statically linked by upstream's default build
        "with_icu": True,
        "with_tpch": False,
        "with_tpcds": False,
        "with_json": True,
        "with_query_log": False,
        "with_shell": False,
        "with_threads": True,
        "with_rdtsc": False,
        "with_extension_load": True,
        "with_httplib": True,
        "with_jemalloc": True,
    }
    short_paths = True

    def export_sources(self):
        copy(self, "cmake/*", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        # jemalloc is an allocator switch, used on 64-bit Linux only
        if self.settings.os != "Linux" or self.settings.arch not in ["x86_64", "armv8"]:
            del self.options.with_jemalloc

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.with_extension_load:
            # Upstream turns the built-in HTTP client off without extension loading (CMakeLists.txt)
            self.options.rm_safe("with_httplib")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 17)
        # FIXME: drop support MSVC debug shared build
        if is_msvc(self) and self.options.shared and self.settings.build_type == "Debug":
            raise ConanInvalidConfiguration(f"{self.ref} does not support MSVC debug shared build")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    @property
    def _extensions(self):
        return [name for name in ["autocomplete", "tpch", "tpcds", "json", "icu"] if self.options.get_safe(f"with_{name}")]

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["DUCKDB_MAJOR_VERSION"] = Version(self.version).major
        tc.variables["DUCKDB_MINOR_VERSION"] = Version(self.version).minor
        tc.variables["DUCKDB_PATCH_VERSION"] = Version(self.version).patch
        tc.variables["DUCKDB_DEV_ITERATION"] = 0
        tc.variables["OVERRIDE_GIT_DESCRIBE"] = f"v{self.version}"

        tc.variables["BUILD_EXTENSIONS"] = ";".join(self._extensions)
        # Extensions are only linked when listed; the list replaces upstream's default
        # (core_functions, parquet, json, icu), so with_json/with_icu=False take effect
        tc.variables["STATICALLY_LINK_EXTENSIONS"] = ";".join(["core_functions", "parquet"] + self._extensions)
        with_httplib = bool(self.options.get_safe("with_httplib", False))
        tc.variables["ENABLE_EXTENSION_LOAD"] = self.options.with_extension_load
        tc.variables["ENABLE_BUILTIN_HTTPLIB"] = with_httplib
        # Leave out the local_extension_repository capability: it points automatic installs at the build tree
        capabilities = [name for name, enabled in [("httplib", with_httplib),
                                                   ("loadable_extensions", self.options.with_extension_load)]
                        if enabled]
        tc.variables["DUCKDB_CAPABILITIES"] = ";".join(capabilities) or "none"
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
        if is_msvc(self) and self.settings.build_type == "Debug":
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
            # https://github.com/duckdb/duckdb/issues/2805#issuecomment-1013889896
            tc.extra_cxxflags.append("/Zc:__cplusplus")
        tc.generate()

        dpes = CMakeDeps(self)
        dpes.generate()

    def build(self):
        # Upstream forces the static MSVC runtime; let the profile's compiler.runtime decide
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        'set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")',
                        "")
        if not self.options.shared:
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

        # Upstream installs the C++ API archive for its CMake export set, but not its header
        # (tools/cpp/duckdb_cpp.hpp), so consumers cannot use it
        rm(self, "*duckdb_cpp_api.*", os.path.join(self.package_folder, "lib"))
        if self.options.shared:
            # The static libraries, extensions included, are all linked into the shared library
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
            # The loader references the extensions and capabilities, which depend on duckdb_static
            libs = ["duckdb_static_extension_loader"]
            libs += [f"{name}_extension" for name in self._extensions]
            libs += ["core_functions_extension", "parquet_extension"]
            if self.options.get_safe("with_httplib"):
                libs.append("duckdb_httplib")
            if self.options.with_extension_load:
                libs.append("duckdb_loadable_extensions")
            libs.append("duckdb_static")
            libs += ["duckdb_fmt", "duckdb_re2", "duckdb_miniz", "duckdb_utf8proc", "duckdb_hyperloglog",
                     "duckdb_fastpforlib", "duckdb_mbedtls", "duckdb_fsst", "duckdb_zstd",
                     "duckdb_skiplistlib", "duckdb_yyjson"]
            if self.options.get_safe("with_jemalloc"):
                libs.append("duckdb_jemalloc")
            self.cpp_info.libs = libs
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

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "dl", "m"])

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")
            self.cpp_info.system_libs.extend(["rstrtmgr", "bcrypt"])
