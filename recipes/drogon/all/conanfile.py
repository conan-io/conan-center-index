from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import functools

required_conan_version = ">=1.43.0"

class DrogonConan(ConanFile):
    name = "drogon"
    description = "A C++14/17/20 based HTTP web application framework running on Linux/macOS/Unix/Windows"
    topics = ("http-server", "non-blocking-io", "http-framework", "asynchronous-programming")
    license = "MIT"
    homepage = "https://github.com/drogonframework/drogon"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"
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
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "14")

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.Version(self.settings.compiler.version) < minimum_version:
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
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_CTL"] = self.options.with_ctl
        cmake.definitions["BUILD_EXAMPLES"] = False
        cmake.definitions["BUILD_ORM"] = self.options.with_orm
        cmake.definitions["COZ_PROFILING"] = self.options.with_profile
        cmake.definitions["BUILD_DROGON_SHARED"] = self.options.shared
        cmake.definitions["BUILD_DOC"] = False
        cmake.definitions["BUILD_BROTLI"] = self.options.with_brotli
        cmake.definitions["BUILD_POSTGRESQL"] = self.options.get_safe("with_postgres", False)
        cmake.definitions["BUILD_POSTGRESQL_BATCH"] = self.options.get_safe("with_postgres_batch", False)
        cmake.definitions["BUILD_MYSQL"] = self.options.get_safe("with_mysql", False)
        cmake.definitions["BUILD_SQLITE"] = self.options.get_safe("with_sqlite", False)
        cmake.definitions["BUILD_REDIS"] = self.options.get_safe("with_redis", False)
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", "licenses", self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["drogon"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["rpcrt4", "ws2_32", "crypt32", "advapi32"])
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version).major == "8":
            self.cpp_info.system_libs.append("stdc++fs")

        if self.options.with_ctl:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)

        self.cpp_info.set_property("cmake_file_name", "Drogon")
        self.cpp_info.set_property("cmake_target_name", "Drogon::Drogon")

        self.cpp_info.filenames["cmake_find_package"] = "Drogon"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Drogon"
        self.cpp_info.names["cmake_find_package"] = "Drogon"
        self.cpp_info.names["cmake_find_package_multi"] = "Drogon"
