import os
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import cmake_layout, CMakeToolchain, CMakeDeps, CMake
from conan.tools.files import copy, get, export_conandata_patches, rm, save, apply_conandata_patches
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=2.0"


class DrogonConan(ConanFile):
    name = "drogon"
    description = "A C++14/17/20 based HTTP web application framework running on Linux/macOS/Unix/Windows"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/drogonframework/drogon"
    topics = ("http-server", "non-blocking-io", "http-framework", "asynchronous-programming")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [False, True],
        "fPIC": [True, False],
        "with_boost": [True, False],
        "with_ctl": [True, False],
        "with_orm": [True, False],
        "with_profile": [True, False],
        "with_brotli": [True, False],
        "with_yaml_cpp": [True, False],
        "with_postgres": [True, False],
        "with_postgres_batch": [True, False],
        "with_mysql": [True, False],
        "with_sqlite": [True, False],
        "with_redis": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_boost": True,
        "with_ctl": False,
        "with_orm": True,
        "with_profile": False,
        "with_brotli": False,
        "with_yaml_cpp": False,
        "with_postgres": False,
        "with_postgres_batch": False,
        "with_mysql": False,
        "with_sqlite": False,
        "with_redis": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "1.8.4":
            del self.options.with_yaml_cpp

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
            self.options["trantor"].shared = True
        if not self.options.with_orm:
            del self.options.with_postgres
            del self.options.with_postgres_batch
            del self.options.with_mysql
            del self.options.with_sqlite
            del self.options.with_redis
        elif not self.options.with_postgres:
            del self.options.with_postgres_batch

    @property
    def _min_cppstd(self):
        return 14 if Version(self.version) < "1.8.2" else 17

    def validate(self):
        check_min_cppstd(self, 14)
        if self.settings.compiler.cppstd in ["14", "gnu14"] and not self.options.with_boost:
            raise ConanInvalidConfiguration(f"{self.ref} requires boost on C++14")

    def requirements(self):
        if Version(self.version) < "1.9.7":
            self.requires("trantor/1.5.19", transitive_headers=True, transitive_libs=True)
        else:
            self.requires("trantor/1.5.21", transitive_headers=True, transitive_libs=True)
        self.requires("jsoncpp/1.9.5", transitive_headers=True, transitive_libs=True)
        self.requires("openssl/[>=1.1 <4]")
        self.requires("zlib/[>=1.2.11 <2]")
        if self.settings.os == "Linux":
            self.requires("util-linux-libuuid/2.39.2")
        if self.options.with_profile:
            self.requires("coz/cci.20210322")
        if self.options.with_boost:
            self.requires("boost/1.83.0", transitive_headers=True)
        if self.options.with_brotli:
            self.requires("brotli/1.1.0")
        if self.options.get_safe("with_postgres"):
            self.requires("libpq/15.4")
        if self.options.get_safe("with_mysql"):
            self.requires("libmysqlclient/8.1.0")
        if self.options.get_safe("with_sqlite"):
            self.requires("sqlite3/[>=3.45.0 <4]")
        if self.options.get_safe("with_redis"):
            self.requires("hiredis/1.2.0")
        if self.options.get_safe("with_yaml_cpp"):
            self.requires("yaml-cpp/0.8.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_CTL"] = self.options.with_ctl
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_ORM"] = self.options.with_orm
        tc.variables["COZ_PROFILING"] = self.options.with_profile
        tc.variables["BUILD_DROGON_SHARED"] = self.options.shared
        tc.variables["BUILD_DOC"] = False
        tc.variables["BUILD_BROTLI"] = self.options.with_brotli
        tc.variables["BUILD_YAML_CONFIG"] = self.options.get_safe("with_yaml_cpp", False)
        tc.variables["BUILD_POSTGRESQL"] = self.options.get_safe("with_postgres", False)
        tc.variables["BUILD_POSTGRESQL_BATCH"] = self.options.get_safe("with_postgres_batch", False)
        tc.variables["BUILD_MYSQL"] = self.options.get_safe("with_mysql", False)
        tc.variables["BUILD_SQLITE"] = self.options.get_safe("with_sqlite", False)
        tc.variables["BUILD_REDIS"] = self.options.get_safe("with_redis", False)
        if is_msvc(self):
            tc.extra_cxxflags("/Zc:__cplusplus /EHsc")
        if Version(self.version) >= "1.8.4":
            tc.variables["USE_SUBMODULE"] = False
        # Required for tc.variables to work reliably on v3.5 < v3.12 CMake standard used by the project
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        cmake_folder = os.path.join(self.package_folder, "lib", "cmake", "Drogon")
        rm(self, "DrogonConfig*.cmake", cmake_folder)
        rm(self, "DrogonTargets*.cmake", cmake_folder)
        rm(self, "Find*.cmake", cmake_folder)
        # https://github.com/drogonframework/drogon/blob/v1.9.6/cmake/templates/DrogonConfig.cmake.in#L60-L62
        save(self, os.path.join(cmake_folder, "conan-official-variables.cmake"),
             textwrap.dedent("""\
                 set(DROGON_INCLUDE_DIRS "${${CMAKE_FIND_PACKAGE_NAME}_INCLUDE_DIRS}")
                 set(DROGON_LIBRARIES "${${CMAKE_FIND_PACKAGE_NAME}_LIBRARIES}")
                 set(DROGON_EXECUTABLE drogon_ctl)
                 """)
        )

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Drogon")
        self.cpp_info.set_property("cmake_target_name", "Drogon::Drogon")

        self.cpp_info.libs = ["drogon"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["rpcrt4", "ws2_32", "crypt32", "advapi32"])
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version).major == "8":
            self.cpp_info.system_libs.append("stdc++fs")

        # Include official CMake modules and exported CMake variables
        # https://github.com/drogonframework/drogon/blob/v1.9.6/cmake/templates/DrogonConfig.cmake.in#L55-L57
        cmake_folder = os.path.join("lib", "cmake", "Drogon")
        modules = [
            os.path.join(cmake_folder, "conan-official-variables.cmake"),
            os.path.join(cmake_folder, "DrogonUtilities.cmake"),
            os.path.join(cmake_folder, "ParseAndAddDrogonTests.cmake"),
        ]
        self.cpp_info.builddirs.append(cmake_folder)
        self.cpp_info.set_property("cmake_build_modules", modules)
