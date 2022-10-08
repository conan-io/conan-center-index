from conan import ConanFile
from conan.tools.cmake import cmake_layout, CMakeToolchain, CMakeDeps, CMake
from conan.tools.files import copy, get, apply_conandata_patches, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os


required_conan_version = ">=1.50.2 <1.51.0 || >=1.51.2"

class DrogonConan(ConanFile):
    name = "drogon"
    description = "A C++14/17/20 based HTTP web application framework running on Linux/macOS/Unix/Windows"
    topics = ("http-server", "non-blocking-io", "http-framework", "asynchronous-programming")
    license = "MIT"
    homepage = "https://github.com/drogonframework/drogon"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [False, True],
        "fPIC": [True, False],
        "with_boost": [True, False],
        "with_ctl": [True, False],
        "with_orm": [True, False],
        "with_profile": [True, False],
        "with_brotli": [True, False],
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
        "with_postgres": False,
        "with_postgres_batch": False,
        "with_mysql": False,
        "with_sqlite": False,
        "with_redis": False,
    }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
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
    def _compilers_minimum_version(self):
        return {
            "gcc": "6",
            "Visual Studio": "15.0",
            "clang": "5",
            "apple-clang": "10",
        }

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, "14")

        minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
        if minimum_version:
            if Version(self.info.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("{} requires C++14, which your compiler does not support.".format(self.name))
        else:
            self.output.warn("{} requires C++14. Your compiler is unknown. Assuming it supports C++14.".format(self.name))

    def requirements(self):
        self.requires("trantor/1.5.6")
        self.requires("jsoncpp/1.9.5")
        self.requires("openssl/1.1.1q")
        self.requires("zlib/1.2.12")
        if self.settings.os == "Linux":
            self.requires("libuuid/1.0.3")
        if self.options.with_profile:
            self.requires("coz/cci.20210322")
        if self.options.with_boost:
            self.requires("boost/1.79.0")
        if self.options.with_brotli:
            self.requires("brotli/1.0.9")
        if self.options.get_safe("with_postgres"):
            self.requires("libpq/14.2")
        if self.options.get_safe("with_mysql"):
            self.requires("libmysqlclient/8.0.25")
        if self.options.get_safe("with_sqlite"):
            self.requires("sqlite3/3.39.2")
        if self.options.get_safe("with_redis"):
            self.requires("hiredis/1.0.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

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
        tc.variables["BUILD_POSTGRESQL"] = self.options.get_safe("with_postgres", False)
        tc.variables["BUILD_POSTGRESQL_BATCH"] = self.options.get_safe("with_postgres_batch", False)
        tc.variables["BUILD_MYSQL"] = self.options.get_safe("with_mysql", False)
        tc.variables["BUILD_SQLITE"] = self.options.get_safe("with_sqlite", False)
        tc.variables["BUILD_REDIS"] = self.options.get_safe("with_redis", False)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["drogon"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["rpcrt4", "ws2_32", "crypt32", "advapi32"])
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version).major == "8":
            self.cpp_info.system_libs.append("stdc++fs")

        if self.options.with_ctl:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)

        self.cpp_info.set_property("cmake_file_name", "Drogon")
        self.cpp_info.set_property("cmake_target_name", "Drogon::Drogon")

        # TODO: Remove after Conan 2.0
        self.cpp_info.filenames["cmake_find_package"] = "Drogon"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Drogon"
        self.cpp_info.names["cmake_find_package"] = "Drogon"
        self.cpp_info.names["cmake_find_package_multi"] = "Drogon"
