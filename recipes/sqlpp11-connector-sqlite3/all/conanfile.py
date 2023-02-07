from conan import ConanFile
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class sqlpp11Conan(ConanFile):
    name = "sqlpp11-connector-sqlite3"
    description = "A C++ wrapper for sqlite3 meant to be used in combination with sqlpp11."
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rbock/sqlpp11-connector-sqlite3"
    topics = ("conan", "sqlpp11-connector-sqlite3", "sqlite3", "sqlpp11", "sql", "database")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_sqlcipher": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_sqlcipher": False,
    }
    short_paths = True

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("sqlpp11/0.60")
        if Version(self.version) < "0.31.0":
            self.requires("date/3.0.1")
        if self.options.with_sqlcipher:
            self.requires("sqlcipher/4.5.1")
        else:
            self.requires("sqlite3/3.40.1")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) < "0.31.0":
            tc.variables["ENABLE_TESTS"] = False
        else:
            tc.variables["ENABLE_TESTING"] = False
        tc.variables["SQLCIPHER"] = self.options.with_sqlcipher
        tc.variables["SQLPP11_INCLUDE_DIR"] = self.deps_cpp_info["sqlpp11"].include_paths[0].replace("\\", "/")
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["sqlpp11-connector-sqlite3"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
        if self.options.with_sqlcipher:
            self.cpp_info.defines = ["SQLPP_USE_SQLCIPHER"]
