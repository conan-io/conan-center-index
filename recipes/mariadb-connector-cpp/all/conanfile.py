from conan import ConanFile, tools
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import files, get, copy, replace_in_file, collect_libs
from conan.errors import ConanInvalidConfiguration
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
        "fPIC": [True, False]
    }
    
    default_options = {
        "shared": False, 
        "fPIC": True
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

        # To install relocatable shared libs on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"

        tc.generate()

    def requirements(self):
        self.requires ("mariadb-connector-c/[>=3.1.11 <4]")

    def _patch_sources(self):
        cmake = os.path.join(self.source_folder, "CMakeLists.txt")
        replace_in_file(self, cmake, "CMAKE_MINIMUM_REQUIRED(VERSION 3.23)", "CMAKE_MINIMUM_REQUIRED(VERSION 3.1)")
        replace_in_file(self, cmake, "${MARIADB_CLIENT_TARGET_NAME}", "mariadb-connector-c::mariadb-connector-c")

        # TODO: resolve find mariadb-connector-c
        replace_in_file(self, cmake, "SET(CMAKE_CXX_STANDARD 11)", "SET(CMAKE_CXX_STANDARD 11)\nFIND_PACKAGE(mariadb-connector-c REQUIRED)")

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