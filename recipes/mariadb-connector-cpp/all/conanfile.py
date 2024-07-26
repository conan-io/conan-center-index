from conan import ConanFile, tools
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import files, get, copy, replace_in_file, collect_libs
from conan.errors import ConanInvalidConfiguration
import os
import glob

required_conan_version = ">=1.53.0"

class MariadbConnectorCppRecipe (ConanFile):
    name = "mariadb-connector-cpp"
    version = "1.1.4"
    description = "MariaDB Connector/C++ is used to connect applications " \
                  "developed in C++ to MariaDB and MySQL databases."
    license = "LGPL-2.1-or-later"
    topics = ("mariadb", "mysql", "database")
    homepage = "https://mariadb.com/docs/server/connect/programming-languages/cpp"
    url = "https://github.com/mariadb-corporation/mariadb-connector-cpp"

    package_type = "library"

    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "dyncol": [True, False],
        "with_iconv": [True, False],
        "with_curl": [True, False],
        "with_ssl": [False, "openssl", "gnutls", "schannel"],
    }
    
    default_options = {
        "shared": False, 
        "fPIC": True,
        "dyncol": True,
        "with_iconv": False,
        "with_curl": True,
        "with_ssl": "openssl",
    }

    def source(self):
        get (self, **self.conan_data["sources"][self.version], strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        
        tc.variables["WITH_UNIT_TESTS"] = False
        tc.variables["INSTALL_BINDIR"] = "bin"
        tc.variables["INSTALL_LIBDIR"] = "lib"
        tc.variables["INSTALL_PLUGINDIR"] = os.path.join("lib", "plugin").replace("\\", "/")
        tc.variables["USE_SYSTEM_INSTALLED_LIB"] = True

        tc.generate()

    def requirements(self):
        if self.options.with_curl:
            # precompiled mariadb-connector-c accepts only this version of libcurl
            self.requires ("libcurl/8.6.0")
        
        self.requires ("mariadb-connector-c/3.3.3", options={
            "dyncol": self.options.dyncol, 
            "with_iconv": self.options.with_iconv,
            "with_curl": self.options.with_curl,
            "with_ssl": self.options.with_ssl
        })

    def _patch_sources(self):
        cmake = os.path.join(self.source_folder, "CMakeLists.txt")
        replace_in_file(self, cmake, "CMAKE_MINIMUM_REQUIRED(VERSION 3.23)", "CMAKE_MINIMUM_REQUIRED(VERSION 3.1)", strict=False)
        replace_in_file(self, cmake, "FIND_LIBRARY(CCLIB libmariadb.so)", "SET(CCLIB mariadb-connector-c::mariadb-connector-c)", strict=False)

        # TODO: resolve find mariadb-connector-c

        # Library
        string = "SET(CMAKE_CXX_STANDARD 11)"
        replace_in_file(self, cmake, string, string + "\nFIND_PACKAGE(mariadb-connector-c REQUIRED)", strict=False)

        # Headers
        string = "IF (${CCHEADER} STREQUAL \"CCHEADER-NOTFOUND\")"
        replace_in_file(self, cmake, string, "FIND_FILE(CCHEADER NAMES \"mysql.h\")\n" + string)

    def build(self):
        self._patch_sources()

        cmake = CMake(self)

        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
            
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "mariadb-connector-cpp")
        self.cpp_info.set_property("cmake_target_name", "mariadb-connector-cpp::mariadb-connector-cpp")
        self.cpp_info.set_property("pkg_config_name", "libmariadb")

        self.cpp_info.libs = collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["dl", "m", "pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "shlwapi"]
            if self.options.with_ssl == "schannel":
                self.cpp_info.system_libs.append("secur32")

        plugin_dir = os.path.join(self.package_folder, "lib", "plugin").replace("\\", "/")
        self.runenv_info.prepend_path("MARIADB_PLUGIN_DIR", plugin_dir)

        self.cpp_info.libs = ["mariadbcpp"]