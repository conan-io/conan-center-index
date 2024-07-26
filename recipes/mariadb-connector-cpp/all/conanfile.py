from conan import ConanFile, tools
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import files, get, copy, replace_in_file, collect_libs, rmdir, rm
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
import os
import glob

required_conan_version = ">=1.53.0"

class MariadbConnectorCppRecipe (ConanFile):
    name = "mariadb-connector-cpp"
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
        "with_curl": [True, False],
        "with_ssl": [False, "openssl", "gnutls", "schannel"],
    }
    
    default_options = {
        "shared": False, 
        "fPIC": True,
        "dyncol": True,
        "with_curl": True,
        "with_ssl": "openssl",
    }

    def source(self):
        get (self, **self.conan_data["sources"][self.version], strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
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
        tc.variables["MARIADB_LINK_DYNAMIC"] = True

        # To install relocatable shared libs on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"

        tc.generate()

    def requirements(self):
        if self.options.with_curl:
            # precompiled mariadb-connector-c accepts only this version of libcurl
            self.requires ("libcurl/8.6.0")
        
        # with_iconv doesn't exists on Windows (Why?)
        self.requires ("mariadb-connector-c/3.3.3", options={
            "dyncol": self.options.dyncol,
            "with_curl": self.options.with_curl,
            "with_ssl": self.options.with_ssl
        })

    def _patch_sources(self):
        cmake = os.path.join(self.source_folder, "CMakeLists.txt")
        replace_in_file(self, cmake, "CMAKE_MINIMUM_REQUIRED(VERSION 3.23)", "CMAKE_MINIMUM_REQUIRED(VERSION 3.1)")
        replace_in_file(self, cmake, "FIND_LIBRARY(CCLIB libmariadb.so)", "SET(CCLIB mariadb-connector-c::mariadb-connector-c)")

        # TODO: resolve find mariadb-connector-c

        # Library
        string = "SET(CMAKE_CXX_STANDARD 11)"
        replace_in_file(self, cmake, string, string + "\nFIND_PACKAGE(mariadb-connector-c REQUIRED)")

        # Headers
        string = "IF (${CCHEADER} STREQUAL \"CCHEADER-NOTFOUND\")"
        replace_in_file(self, cmake, string, "FIND_FILE(CCHEADER NAMES \"mysql.h\")\n" + string)
        
        # MARIADB_LINK_DYNAMIC
        options_cmake = os.path.join (self.source_folder, "cmake", "options_defaults.cmake")

        string = "OPTION(MARIADB_LINK_DYNAMIC \"Link Connector/C library dynamically\" "
        replace_in_file(self, options_cmake, string + "OFF)", string + "ON)")
        replace_in_file(self, options_cmake, "SET(MARIADB_LINK_DYNAMIC OFF)", "SET(MARIADB_LINK_DYNAMIC ON)")

    def build(self):
        self._patch_sources()

        cmake = CMake(self)

        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        fix_apple_shared_install_name(self)

    def package_info(self):
            
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "mariadb-connector-cpp")
        self.cpp_info.set_property("cmake_target_name", "mariadb-connector-cpp::mariadb-connector-cpp")
        self.cpp_info.set_property("pkg_config_name", "libmariadbcpp")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["dl", "m", "pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "shlwapi"]
            if self.options.with_ssl == "schannel":
                self.cpp_info.system_libs.append("secur32")

        self.cpp_info.libs = ["mariadbcpp"]