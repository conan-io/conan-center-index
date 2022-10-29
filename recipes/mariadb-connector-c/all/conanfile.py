from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, get, replace_in_file, rm, rmdir
import os

required_conan_version = ">=1.51.1"


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

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_iconv
            self.options.with_ssl = "schannel"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def requirements(self):
        self.requires("zlib/1.2.12")
        if self.options.get_safe("with_iconv"):
            self.requires("libiconv/1.17")
        if self.options.with_curl:
            self.requires("libcurl/7.84.0")
        if self.options.with_ssl == "openssl":
            self.requires("openssl/1.1.1q")

    def validate(self):
        if self.info.settings.os != "Windows" and self.info.options.with_ssl == "schannel":
            raise ConanInvalidConfiguration("schannel only supported on Windows")
        if self.info.options.with_ssl == "gnutls":
            raise ConanInvalidConfiguration("gnutls not yet available in CCI")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.settings.os == "Windows":
            tc.variables["WITH_MSI"] = False
            tc.variables["WITH_SIGNCODE"] = False
            tc.variables["WITH_RTC"] = False
        else:
            tc.variables["WITH_MYSQLCOMPAT"] = False
            tc.variables["WITH_ICONV"] = self.options.with_iconv
        tc.variables["WITH_UNIT_TESTS"] = False
        tc.variables["WITH_DYNCOL"] = self.options.dyncol
        tc.variables["WITH_EXTERNAL_ZLIB"] = True
        tc.variables["WITH_CURL"] = self.options.with_curl
        tc.variables["WITH_SSL"] = self.options.with_ssl
        tc.variables["INSTALL_BINDIR"] = "bin"
        tc.variables["INSTALL_LIBDIR"] = "lib"
        tc.variables["INSTALL_PLUGINDIR"] = os.path.join("lib", "plugin").replace("\\", "/")
        # To install relocatable shared libs on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        root_cmake = os.path.join(self.source_folder, "CMakeLists.txt")
        replace_in_file(self, root_cmake, "${ZLIB_LIBRARY}", "${ZLIB_LIBRARIES}")
        replace_in_file(self,
            root_cmake,
            "SET(SSL_LIBRARIES ${OPENSSL_SSL_LIBRARY} ${OPENSSL_CRYPTO_LIBRARY})",
            "SET(SSL_LIBRARIES OpenSSL::SSL OpenSSL::Crypto)"
        )
        replace_in_file(self, root_cmake, "${CURL_LIBRARIES}", "CURL::libcurl")
        plugins_io_cmake = os.path.join(self.source_folder, "plugins", "io", "CMakeLists.txt")
        replace_in_file(self, plugins_io_cmake, "${CURL_LIBRARIES}", "CURL::libcurl")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING.LIB", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "symbols"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libmariadb")
        self.cpp_info.includedirs.append(os.path.join("include", "mariadb"))
        self.cpp_info.libs = collect_libs(self)
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
