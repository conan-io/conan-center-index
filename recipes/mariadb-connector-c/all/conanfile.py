from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.29.1"


class MariadbConnectorcConan(ConanFile):
    name = "mariadb-connector-c"
    description = "MariaDB Connector/C is used to connect applications " \
                  "developed in C/C++ to MariaDB and MySQL databases."
    license = "LGPL-2.1-or-later"
    topics = ("conan", "mariadb-connector-c", "mariadb", "mysql", "database")
    homepage = "https://mariadb.com/kb/en/mariadb-connector-c"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "dyncol": [True, False],
        "with_iconv": [True, False],
        "with_curl": [True, False],
        "with_ssl": [False, "openssl", "gnutls", "schannel"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "dyncol": True,
        "with_iconv": False,
        "with_curl": True,
        "with_ssl": "openssl"
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_iconv
            self.options.with_ssl = "schannel"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os != "Windows" and self.options.with_ssl == "schannel":
            raise ConanInvalidConfiguration("schannel only supported on Windows")

    def requirements(self):
        self.requires("zlib/1.2.11")
        if self.options.get_safe("with_iconv"):
            self.requires("libiconv/1.16")
        if self.options.with_curl:
            self.requires("libcurl/7.75.0")
        if self.options.with_ssl == "openssl":
            self.requires("openssl/1.1.1k")
        elif self.options.with_ssl == "gnutls":
            raise ConanInvalidConfiguration("gnutls not yet available in CCI")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "mariadb-connector-c-{}-src".format(self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        root_cmake = os.path.join(self._source_subfolder, "CMakeLists.txt")
        tools.replace_in_file(root_cmake, "${ZLIB_LIBRARY}", "${ZLIB_LIBRARIES}")
        tools.replace_in_file(
            root_cmake,
            "SET(SSL_LIBRARIES ${OPENSSL_SSL_LIBRARY} ${OPENSSL_CRYPTO_LIBRARY})",
            "SET(SSL_LIBRARIES ${OPENSSL_LIBRARIES})"
        )

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if self.settings.os == "Windows":
            self._cmake.definitions["WITH_MSI"] = False
            self._cmake.definitions["WITH_SIGNCODE"] = False
            self._cmake.definitions["WITH_RTC"] = False
        else:
            self._cmake.definitions["WITH_MYSQLCOMPAT"] = False
            self._cmake.definitions["WITH_ICONV"] = self.options.with_iconv
        self._cmake.definitions["WITH_UNIT_TESTS"] = False
        self._cmake.definitions["WITH_DYNCOL"] = self.options.dyncol
        self._cmake.definitions["WITH_EXTERNAL_ZLIB"] = True
        self._cmake.definitions["WITH_CURL"] = self.options.with_curl
        self._cmake.definitions["WITH_SSL"] = self.options.with_ssl
        self._cmake.definitions["INSTALL_BINDIR"] = "bin"
        self._cmake.definitions["INSTALL_LIBDIR"] = "lib"
        self._cmake.definitions["INSTALL_PLUGINDIR"] = os.path.join("lib", "plugin").replace("\\", "/")
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING.LIB", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "symbols"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.pdb")

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libmariadb"
        self.cpp_info.includedirs.append(os.path.join("include", "mariadb"))
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl", "m", "pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "shlwapi"]
            if self.options.with_ssl == "schannel":
                self.cpp_info.system_libs.append("secur32")

        plugin_dir = os.path.join(self.package_folder, "lib", "plugin").replace("\\", "/")
        self.output.info("Creating MARIADB_PLUGIN_DIR environment variable: {}".format(plugin_dir))
        self.env_info.MARIADB_PLUGIN_DIR = plugin_dir
