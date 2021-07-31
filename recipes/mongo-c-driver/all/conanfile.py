from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class MongoCDriverConan(ConanFile):
    name = "mongo-c-driver"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://mongoc.org/"
    description = "A Cross Platform MongoDB Client Library for C"
    topics = ("conan", "libbson", "libmongoc", "mongo", "mongodb", "database", "db")
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package", "pkg_config"
    short_paths = True
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ssl": [False, "darwin", "windows", "openssl", "libressl"],
        "with_sasl": [False, "sspi", "cyrus"],
        "with_snappy": [True, False],
        "with_zlib": [True, False],
        "with_zstd": [True, False],
        "with_icu": [True, False],
        "srv": [True, False]
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssl": "openssl",
        "with_sasl": False,
        "with_snappy": True,
        "with_zlib": True,
        "with_zstd": True,
        "with_icu": True,
        "srv": True
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            self.options.with_sasl = "sspi"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC
        if self.options.with_ssl == "darwin" and not tools.is_apple_os(self.settings.os):
            raise ConanInvalidConfiguration("with_ssl=darwin only allowed on Apple os family")
        if self.options.with_ssl == "windows" and self.settings.os != "Windows":
            raise ConanInvalidConfiguration("with_ssl=windows only allowed on Windows")
        if self.options.with_sasl == "sspi" and self.settings.os != "Windows":
            raise ConanInvalidConfiguration("with_sasl=sspi only allowed on Windows")

    def requirements(self):
        if self.options.with_ssl == "openssl":
            self.requires("openssl/1.1.1k")
        elif self.options.with_ssl == "libressl":
            self.requires("libressl/3.2.1")
        if self.options.with_sasl == "cyrus":
            self.requires("cyrus-sasl/2.1.27")
        if self.options.with_snappy:
            self.requires("snappy/1.1.9")
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.with_zstd:
            self.requires("zstd/1.5.0")
        if self.options.with_icu:
            self.requires("icu/69.1")

    def build_requirements(self):
        if self.options.with_ssl == "libressl" or self.options.with_zstd:
            self.build_requires("pkgconf/1.7.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        to_replace_old_new = [
            # Fix Snappy
            {"old": "include (FindSnappy)\nif (SNAPPY_INCLUDE_DIRS)",
             "new": "if(ENABLE_SNAPPY MATCHES \"ON\")\n  find_package(Snappy REQUIRED)"},
            {"old": "SNAPPY_LIBRARIES", "new": "Snappy_LIBRARIES"},
            {"old": "SNAPPY_INCLUDE_DIRS", "new": "Snappy_INCLUDE_DIRS"},
            # Fix LibreSSL
            {"old": "set (SSL_LIBRARIES -ltls -lcrypto)", "new": ""},
        ]
        for old_new in to_replace_old_new:
            tools.replace_in_file(os.path.join(self._source_subfolder, "src", "libmongoc", "CMakeLists.txt"),
                                  old_new["old"], old_new["new"])

    @property
    def _ssl_cmake_value(self):
        return {
            "darwin": "DARWIN",
            "windows": "WINDOWS",
            "openssl": "OPENSSL",
            "libressl": "LIBRESSL",
        }.get(str(self.options.with_ssl), "OFF")

    @property
    def _sasl_cmake_value(self):
        return {
            "sspi": "SSPI",
            "cyrus": "CYRUS",
        }.get(str(self.options.with_sasl), "OFF")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CMAKE_INSTALL_SYSTEM_RUNTIME_LIBS_SKIP"] = "TRUE"
        self._cmake.definitions["ENABLE_SSL"] = self._ssl_cmake_value
        self._cmake.definitions["ENABLE_SASL"] = self._sasl_cmake_value
        self._cmake.definitions["ENABLE_STATIC"] = "OFF" if self.options.shared else "ON"
        self._cmake.definitions["ENABLE_TESTS"] = "OFF"
        self._cmake.definitions["ENABLE_EXAMPLES"] = "OFF"
        self._cmake.definitions["ENABLE_SRV"] = "ON" if self.options.srv else "OFF"
        self._cmake.definitions["ENABLE_MAINTAINER_FLAGS"] = "OFF"
        self._cmake.definitions["ENABLE_AUTOMATIC_INIT_AND_CLEANUP"] = "ON"
        self._cmake.definitions["ENABLE_CRYPTO_SYSTEM_PROFILE"] = "OFF"
        self._cmake.definitions["ENABLE_TRACING"] = "OFF"
        self._cmake.definitions["ENABLE_COVERAGE"] = "OFF"
        self._cmake.definitions["ENABLE_SHM_COUNTERS"] = "OFF"
        self._cmake.definitions["ENABLE_MONGOC"] = "ON"
        self._cmake.definitions["ENABLE_BSON"] = "ON"
        self._cmake.definitions["ENABLE_SNAPPY"] = "ON" if self.options.with_snappy else "OFF"
        self._cmake.definitions["ENABLE_ZLIB"] = "SYSTEM" if self.options.with_zlib else "OFF"
        self._cmake.definitions["ENABLE_ZSTD"] = "ON" if self.options.with_zstd else "OFF"
        self._cmake.definitions["ENABLE_MAN_PAGES"] = False
        self._cmake.definitions["ENABLE_HTML_DOCS"] = False
        self._cmake.definitions["ENABLE_EXTRA_ALIGNMENT"] = True
        self._cmake.definitions["ENABLE_RDTSCP"] = False
        self._cmake.definitions["ENABLE_APPLE_FRAMEWORK"] = False
        self._cmake.definitions["ENABLE_ICU"] = "ON" if self.options.with_icu else "OFF"
        self._cmake.definitions["ENABLE_UNINSTALL"] = False
        self._cmake.definitions["ENABLE_CLIENT_SIDE_ENCRYPTION"] = "OFF"  # libmongocrypt recipe not yet in CCI
        self._cmake.definitions["ENABLE_MONGODB_AWS_AUTH"] = "AUTO"
        self._cmake.definitions["ENABLE_PIC"] = self.options.get_safe("fPIC", True)
        if self.options.with_ssl == "openssl":
            self._cmake.definitions["OPENSSL_ROOT_DIR"] = self.deps_cpp_info["openssl"].rootpath

        self._cmake.configure(build_folder=self._build_subfolder)

        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="THIRD_PARTY_NOTICES", dst="licenses", src=self._source_subfolder)

        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        # FIXME: two CMake module/config files should be generated (mongoc-1.0-config.cmake and bson-1.0-config.cmake),
        # but it can't be modeled right now.
        self.cpp_info.filenames["cmake_find_package"] = "mongoc-1.0"
        self.cpp_info.filenames["cmake_find_package_multi"] = "mongoc-1.0"
        self.cpp_info.names["cmake_find_package"] = "mongo"
        self.cpp_info.names["cmake_find_package_multi"] = "mongo"
        # mongoc
        self.cpp_info.components["mongoc"].names["cmake_find_package"] = "mongoc_shared" if self.options.shared else "mongoc_static"
        self.cpp_info.components["mongoc"].names["cmake_find_package_multi"] = "mongoc_shared" if self.options.shared else "mongoc_static"
        self.cpp_info.components["mongoc"].names["pkg_config"] = "libmongoc-1.0" if self.options.shared else "libmongoc-static-1.0"
        self.cpp_info.components["mongoc"].includedirs = [os.path.join("include", "libmongoc-1.0")]
        self.cpp_info.components["mongoc"].libs = ["mongoc-1.0" if self.options.shared else "mongoc-static-1.0"]
        if not self.options.shared:
            self.cpp_info.components["mongoc"].defines = ["MONGOC_STATIC"]
        self.cpp_info.components["mongoc"].requires = ["bson"]
        if self.settings.os == "Windows":
            self.cpp_info.components["mongoc"].system_libs.append("ws2_32")
        if self.options.with_ssl == "darwin":
            self.cpp_info.components["mongoc"].frameworks.extend(["CoreFoundation", "Security"])
        elif self.options.with_ssl == "windows":
            self.cpp_info.components["mongoc"].system_libs.extend(["secur32", "crypt32", "bcrypt"])
        elif self.options.with_ssl == "openssl":
            self.cpp_info.components["mongoc"].requires.append("openssl::openssl")
        elif self.options.with_ssl == "libressl":
            self.cpp_info.components["mongoc"].requires.append("libressl::libressl")
        if self.options.with_sasl == "sspi":
            self.cpp_info.components["mongoc"].system_libs.extend(["secur32", "crypt32", "shlwapi"])
        elif self.options.with_sasl == "cyrus":
            self.cpp_info.components["mongoc"].requires.append("cyrus-sasl::cyrus-sasl")
        if self.options.with_snappy:
            self.cpp_info.components["mongoc"].requires.append("snappy::snappy")
        if self.options.with_zlib:
            self.cpp_info.components["mongoc"].requires.append("zlib::zlib")
        if self.options.with_zstd:
            self.cpp_info.components["mongoc"].requires.append("zstd::zstd")
        if self.options.with_icu:
            self.cpp_info.components["mongoc"].requires.append("icu::icu")
        if self.options.srv:
            self.cpp_info.components["mongoc"].system_libs.append("dnsapi" if self.settings.os == "Windows" else "resolv")
        # bson
        self.cpp_info.components["bson"].names["cmake_find_package"] = "bson_shared" if self.options.shared else "bson_static"
        self.cpp_info.components["bson"].names["cmake_find_package_multi"] = "bson_shared" if self.options.shared else "bson_static"
        self.cpp_info.components["bson"].names["pkg_config"] = "libbson-1.0" if self.options.shared else "libbson-static-1.0"
        self.cpp_info.components["bson"].includedirs = [os.path.join("include", "libbson-1.0")]
        self.cpp_info.components["bson"].libs = ["bson-1.0" if self.options.shared else "bson-static-1.0"]
        if not self.options.shared:
            self.cpp_info.components["bson"].defines = ["BSON_STATIC"]
        if self.settings.os == "Linux":
            self.cpp_info.components["bson"].system_libs = ["m", "pthread", "rt"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["bson"].system_libs = ["ws2_32"]
