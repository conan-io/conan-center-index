from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.36.0"


class MariadbConnectorcConan(ConanFile):
    name = "mariadb-connector-c"
    description = "MariaDB Connector/C is used to connect applications " \
                  "developed in C/C++ to MariaDB and MySQL databases."
    license = "LGPL-2.1-or-later"
    topics = ("mariadb", "mysql", "database")
    homepage = "https://mariadb.com/kb/en/mariadb-connector-c"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
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

    generators = "cmake", "cmake_find_package"
    _cmake = None

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
            del self.options.with_iconv
            self.options.with_ssl = "schannel"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("zlib/1.2.12")
        if self.options.get_safe("with_iconv"):
            self.requires("libiconv/1.17")
        if self.options.with_curl:
            self.requires("libcurl/7.84.0")
        if self.options.with_ssl == "openssl":
            self.requires("openssl/1.1.1q")

    def validate(self):
        if self.settings.os != "Windows" and self.options.with_ssl == "schannel":
            raise ConanInvalidConfiguration("schannel only supported on Windows")
        if self.options.with_ssl == "gnutls":
            raise ConanInvalidConfiguration("gnutls not yet available in CCI")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

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
        # To install relocatable shared libs on Macos
        self._cmake.definitions["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
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
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "symbols"))
        tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.pdb")

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libmariadb")
        self.cpp_info.includedirs.append(os.path.join("include", "mariadb"))
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["dl", "m", "pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "shlwapi"]
            if self.options.with_ssl == "schannel":
                self.cpp_info.system_libs.append("secur32")

        plugin_dir = os.path.join(self.package_folder, "lib", "plugin").replace("\\", "/")
        self.output.info("Prepending to MARIADB_PLUGIN_DIR runtime environment variable: {}".format(plugin_dir))
        self.runenv_info.prepend_path("MARIADB_PLUGIN_DIR", plugin_dir)

        # TODO: to remove in conan v2?
        self.cpp_info.names["pkg_config"] = "libmariadb"
        self.env_info.MARIADB_PLUGIN_DIR.append(plugin_dir)
