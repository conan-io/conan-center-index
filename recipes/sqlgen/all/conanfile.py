from conan import ConanFile
from conan.tools.files import get, copy, rmdir
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps


from conan.tools.env import VirtualBuildEnv
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

import os

required_conan_version = ">=2.18.1"


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
        "with_postgres": [True, False],
        "with_sqlite3": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_postgres": True,
        "with_sqlite3": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("reflect-cpp/0.19.0", transitive_headers=True)
        if self.options.with_postgres:
            self.requires("libpq/17.5", transitive_headers=True)
        if self.options.with_sqlite3:
            self.requires("sqlite3/3.49.1", transitive_headers=True)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.23 <4]")

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def layout(self):
        cmake_layout(self, src_folder=".")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["SQLGEN_BUILD_SHARED"] = self.options.shared
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

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "17",
            "msvc": "1938",
            "gcc": "11",
            "clang": "13",
            "apple-clang": "15",
        }
