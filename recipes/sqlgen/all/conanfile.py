from conan import ConanFile
from conan.tools.files import get, copy, rmdir
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.build import check_min_cppstd

import os

required_conan_version = ">=2.1"


class SQLGenConan(ConanFile):
    name = "sqlgen"
    description = "sqlgen is an ORM and SQL query generator for C++-20, similar to Python's SQLAlchemy/SQLModel or Rust's Diesel."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/getml/sqlgen"
    topics = ("postgres", "sqlite", "orm")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_mysql": [True, False],
        "with_postgres": [True, False],
        "with_sqlite3": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_mysql": False,
        "with_postgres": True,
        "with_sqlite3": True,
    }
    implements = ["auto_shared_fpic"]

    def requirements(self):
        self.requires("reflect-cpp/0.22.0", transitive_headers=True)
        # All three dependencies fail with undefined symbols without transitive_libs
        if self.options.with_mysql:
            self.requires("mariadb-connector-c/3.4.3", transitive_headers=True, transitive_libs=True)
        if self.options.with_postgres:
            self.requires("libpq/[>=16.4 <18]", transitive_headers=True, transitive_libs=True)
        if self.options.with_sqlite3:
            self.requires("sqlite3/[>=3.49.1 <4]", transitive_headers=True, transitive_libs=True)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.23]")

    def validate(self):
        check_min_cppstd(self, 20)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["SQLGEN_MYSQL"] = self.options.with_mysql
        tc.cache_variables["SQLGEN_POSTGRES"] = self.options.with_postgres
        tc.cache_variables["SQLGEN_SQLITE3"] = self.options.with_sqlite3
        tc.cache_variables["SQLGEN_USE_VCPKG"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            pattern="LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["sqlgen"]
        if self.options.shared:
            self.cpp_info.defines.append("SQLGEN_BUILD_SHARED")
