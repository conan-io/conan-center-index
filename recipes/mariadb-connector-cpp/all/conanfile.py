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
        "fPIC": [True, False],
        "with_curl": [True, False],
        "with_external_zlib": [True, False],
        "with_dyncol": [True, False],
        "with_mysqlcompat": [True, False],
        "with_ssl": [False, "openssl", "gnutls", "schannel"],
        "with_iconv": [True, False],
    }
    
    default_options = {
        "shared": False, 
        "fPIC": True, 
        "with_iconv": True, 
        "with_curl": True, 
        "with_dyncol": True, 
        "with_external_zlib": True, 
        "with_mysqlcompat": False, 
        "with_ssl": "openssl"
    }

    def source(self):
        get (self, **self.conan_data["sources"][self.version]["cpp"], strip_root=True)
        get (self, **self.conan_data["sources"][self.version]["c"], strip_root=False)

        source_cpp = "."
        source_c = glob.glob ("mariadb-connector-c-*")[0]
        
        files.move_folder_contents (self, source_c, os.path.join (source_cpp, "libmariadb"))

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
            self.options.rm_safe("with_iconv")
            self.options.with_ssl = "schannel"

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os != "Windows" and self.options.with_ssl == "schannel":
            raise ConanInvalidConfiguration("schannel only supported on Windows")
        if self.options.with_ssl == "gnutls":
            raise ConanInvalidConfiguration("gnutls not yet available in CCI")

    def generate(self):
        deps = CMakeDeps(self)
        deps.set_property("zstd", "cmake_file_name", "ZSTD")
        deps.generate()

        tc = CMakeToolchain(self)

        if self.settings.os == "Windows":
            tc.variables["WITH_MSI"] = False
            tc.variables["WITH_SIGNCODE"] = False
            tc.variables["WITH_RTC"] = False
        else:
            tc.variables["WITH_MYSQLCOMPAT"] = False
            tc.variables["WITH_ICONV"] = self.options.with_iconv
        
        tc.variables["WITH_UNIT_TESTS"] = False
        tc.variables["WITH_DYNCOL"] = self.options.with_dyncol
        tc.variables["WITH_EXTERNAL_ZLIB"] = self.options.with_external_zlib
        tc.variables["WITH_CURL"] = self.options.with_curl
        tc.variables["WITH_SSL"] = self.options.with_ssl
        tc.variables["INSTALL_BINDIR"] = "bin"
        tc.variables["INSTALL_LIBDIR"] = "lib"
        tc.variables["INSTALL_PLUGINDIR"] = os.path.join("lib", "plugin").replace("\\", "/")

        # To install relocatable shared libs on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"

        tc.generate()

    def requirements(self):
        self.requires("zstd/1.5.5")

        if self.options.get_safe("with_iconv"):
            self.requires("libiconv/1.17")

        if self.options.with_ssl == "openssl":
            self.requires("openssl/[>=1.1 <4]")

        if self.options.with_external_zlib:
            self.requires("zlib/[>=1.2.11 <2]")

        if self.options.with_curl:
            self.requires("libcurl/[>=7.78.0 <9]")

    def _patch_sources(self):
        # C
        root_cmake = os.path.join(self.source_folder, "libmariadb", "CMakeLists.txt")
        replace_in_file(self, root_cmake, "${ZLIB_LIBRARY}", "${ZLIB_LIBRARIES}")
        replace_in_file(self,
            root_cmake,
            "SET(SSL_LIBRARIES ${OPENSSL_SSL_LIBRARY} ${OPENSSL_CRYPTO_LIBRARY})",
            "SET(SSL_LIBRARIES OpenSSL::SSL OpenSSL::Crypto)"
        )
        replace_in_file(self, root_cmake, "${CURL_LIBRARIES}", "CURL::libcurl")
        plugins_io_cmake = os.path.join(self.source_folder, "libmariadb", "plugins", "io", "CMakeLists.txt")
        replace_in_file(self, plugins_io_cmake, "${CURL_LIBRARIES}", "CURL::libcurl")

        # C++
        base_cmake = os.path.join(self.source_folder, "CMakeLists.txt")
        replace_in_file(self, base_cmake, "CMAKE_MINIMUM_REQUIRED(VERSION 3.23)", "CMAKE_MINIMUM_REQUIRED(VERSION 3.1)")

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