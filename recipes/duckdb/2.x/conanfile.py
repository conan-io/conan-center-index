from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, rm, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.microsoft import is_msvc
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout

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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 17)
        # https://github.com/duckdb/duckdb/issues/27645
        if is_msvc(self) and self.settings.build_type == "Debug":
            raise ConanInvalidConfiguration(f"{self.ref} does not support MSVC Debug builds")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # Upstream forces the static MSVC runtime, let the profile's compiler.runtime decide
        # https://github.com/duckdb/duckdb/issues/27643
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        'set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")',
                        "")

    def generate(self):
        tc = CMakeToolchain(self)
        # The tarball has no git metadata, without this upstream reports a dev version
        tc.cache_variables["OVERRIDE_GIT_DESCRIBE"] = f"v{self.version}"
        # Upstream's default profile compiles Release builds for a minimum CPU (-march=x86-64-v3, -mcpu=apple-m1)
        tc.cache_variables["DUCKDB_OPTIMIZATION_PROFILE"] = "NONE"
        # Upstream's default also includes local_extension_repository, which points automatic installs at the build tree
        tc.cache_variables["DUCKDB_CAPABILITIES"] = "httplib loadable_extensions"
        tc.cache_variables["BUILD_SHELL"] = False
        tc.cache_variables["BUILD_UNITTESTS"] = False
        tc.cache_variables["ENABLE_SANITIZER"] = False
        tc.cache_variables["ENABLE_UBSAN"] = False
        if cross_building(self):
            # Must match DuckDBPlatform() in src/include/duckdb/common/platform.hpp
            os_name = {"Macos": "osx", "Android": "linux"}.get(str(self.settings.os), str(self.settings.os).lower())
            arch = {"x86_64": "amd64", "armv8": "arm64", "x86": "i686"}.get(str(self.settings.arch), str(self.settings.arch))
            postfix = "_android" if self.settings.os == "Android" else ""
            tc.cache_variables["DUCKDB_EXPLICIT_PLATFORM"] = f"{os_name}_{arch}{postfix}"
        # INFO: third_party/re2/CMakeLists.txt:24 requires CMake 3.4 for MSVC shared builds
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"
        if is_msvc(self):
            # INFO: Need for MSVC to set correct __cplusplus value
            # https://github.com/duckdb/duckdb/issues/2805#issuecomment-1013889896
            tc.extra_cxxflags.append("/Zc:__cplusplus")
        tc.generate()

    def build(self):
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
        self.cpp_info.set_property("cmake_file_name", "DuckDB")
        self.cpp_info.set_property("cmake_target_name", "duckdb")
        if self.options.shared:
            self.cpp_info.libs = ["duckdb"]
        else:
            self.cpp_info.set_property("cmake_target_aliases", ["duckdb_static"])
            if self.settings.os == "Windows":
                self.cpp_info.defines.append("DUCKDB_STATIC_BUILD")
            self.cpp_info.libs = [
                "core_functions_extension",
                "parquet_extension",
                "json_extension",
                "icu_extension",
                "duckdb_httplib",
                "duckdb_loadable_extensions",
                "duckdb_static",
            ]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "dl", "m"])

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")
            self.cpp_info.system_libs.extend(["rstrtmgr", "bcrypt"])
