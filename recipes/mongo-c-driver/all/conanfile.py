from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os
import functools

required_conan_version = ">=1.43.0"


class MongoCDriverConan(ConanFile):
    name = "mongo-c-driver"
    description = "A Cross Platform MongoDB Client Library for C"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://mongoc.org/"
    topics = ("libbson", "libmongoc", "mongo", "mongodb", "database", "db")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ssl": [False, "darwin", "windows", "openssl", "libressl"],
        "with_sasl": [False, "sspi", "cyrus"],
        "with_snappy": [True, False],
        "with_zlib": [True, False],
        "with_zstd": [True, False],
        "with_icu": [True, False],
        "srv": [True, False],
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
        "srv": True,
    }

    short_paths = True
    generators = "cmake", "cmake_find_package", "pkg_config"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            self.options.with_sasl = "sspi"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_ssl == "openssl":
            self.requires("openssl/1.1.1q")
        elif self.options.with_ssl == "libressl":
            self.requires("libressl/3.5.3")
        if self.options.with_sasl == "cyrus":
            self.requires("cyrus-sasl/2.1.27")
        if self.options.with_snappy:
            self.requires("snappy/1.1.9")
        if self.options.with_zlib:
            self.requires("zlib/1.2.12")
        if self.options.with_zstd:
            self.requires("zstd/1.5.2")
        if self.options.with_icu:
            self.requires("icu/71.1")

    def validate(self):
        if self.options.with_ssl == "darwin" and not tools.is_apple_os(self, self.settings.os):
            raise ConanInvalidConfiguration("with_ssl=darwin only allowed on Apple os family")
        if self.options.with_ssl == "windows" and self.settings.os != "Windows":
            raise ConanInvalidConfiguration("with_ssl=windows only allowed on Windows")
        if self.options.with_sasl == "sspi" and self.settings.os != "Windows":
            raise ConanInvalidConfiguration("with_sasl=sspi only allowed on Windows")

    def build_requirements(self):
        if self.options.with_ssl == "libressl" or self.options.with_zstd:
            self.build_requires("pkgconf/1.7.4")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
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
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "src", "libmongoc", "CMakeLists.txt"),
                                  old_new["old"], old_new["new"])
        # cleanup rpath
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "set (CMAKE_INSTALL_RPATH_USE_LINK_PATH ON)", "")

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

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_INSTALL_SYSTEM_RUNTIME_LIBS_SKIP"] = "TRUE"
        cmake.definitions["ENABLE_SSL"] = self._ssl_cmake_value
        cmake.definitions["ENABLE_SASL"] = self._sasl_cmake_value
        cmake.definitions["ENABLE_STATIC"] = "OFF" if self.options.shared else "ON"
        cmake.definitions["ENABLE_TESTS"] = "OFF"
        cmake.definitions["ENABLE_EXAMPLES"] = "OFF"
        cmake.definitions["ENABLE_SRV"] = "ON" if self.options.srv else "OFF"
        cmake.definitions["ENABLE_MAINTAINER_FLAGS"] = "OFF"
        cmake.definitions["ENABLE_AUTOMATIC_INIT_AND_CLEANUP"] = "ON"
        cmake.definitions["ENABLE_CRYPTO_SYSTEM_PROFILE"] = "OFF"
        cmake.definitions["ENABLE_TRACING"] = "OFF"
        cmake.definitions["ENABLE_COVERAGE"] = "OFF"
        cmake.definitions["ENABLE_SHM_COUNTERS"] = "OFF"
        cmake.definitions["ENABLE_MONGOC"] = "ON"
        cmake.definitions["ENABLE_BSON"] = "ON"
        cmake.definitions["ENABLE_SNAPPY"] = "ON" if self.options.with_snappy else "OFF"
        cmake.definitions["ENABLE_ZLIB"] = "SYSTEM" if self.options.with_zlib else "OFF"
        cmake.definitions["ENABLE_ZSTD"] = "ON" if self.options.with_zstd else "OFF"
        cmake.definitions["ENABLE_MAN_PAGES"] = False
        cmake.definitions["ENABLE_HTML_DOCS"] = False
        cmake.definitions["ENABLE_EXTRA_ALIGNMENT"] = True
        cmake.definitions["ENABLE_RDTSCP"] = False
        cmake.definitions["ENABLE_APPLE_FRAMEWORK"] = False
        cmake.definitions["ENABLE_ICU"] = "ON" if self.options.with_icu else "OFF"
        cmake.definitions["ENABLE_UNINSTALL"] = False
        cmake.definitions["ENABLE_CLIENT_SIDE_ENCRYPTION"] = "OFF"  # libmongocrypt recipe not yet in CCI
        cmake.definitions["ENABLE_MONGODB_AWS_AUTH"] = "AUTO"
        cmake.definitions["ENABLE_PIC"] = self.options.get_safe("fPIC", True)
        if self.options.with_ssl == "openssl":
            cmake.definitions["OPENSSL_ROOT_DIR"] = self.deps_cpp_info["openssl"].rootpath
        if tools.Version(self.version) >= "1.20.0":
            cmake.definitions["MONGO_USE_CCACHE"] = False
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="THIRD_PARTY_NOTICES", dst="licenses", src=self._source_subfolder)

        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        # FIXME: two CMake module/config files should be generated (mongoc-1.0-config.cmake and bson-1.0-config.cmake),
        # but it can't be modeled right now.
        mongoc_target = "mongoc_shared" if self.options.shared else "mongoc_static"
        self.cpp_info.set_property("cmake_file_name", "mongoc-1.0")
        self.cpp_info.set_property("cmake_target_name", "mongo::{}".format(mongoc_target))

        self.cpp_info.filenames["cmake_find_package"] = "mongoc-1.0"
        self.cpp_info.filenames["cmake_find_package_multi"] = "mongoc-1.0"
        self.cpp_info.names["cmake_find_package"] = "mongo"
        self.cpp_info.names["cmake_find_package_multi"] = "mongo"

        # mongoc
        self.cpp_info.components["mongoc"].set_property("cmake_target_name", "mongo::{}".format(mongoc_target))
        self.cpp_info.components["mongoc"].set_property("pkg_config_name", "libmongoc-1.0" if self.options.shared else "libmongoc-static-1.0")

        self.cpp_info.components["mongoc"].names["cmake_find_package"] = mongoc_target
        self.cpp_info.components["mongoc"].names["cmake_find_package_multi"] = mongoc_target

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
        bson_target = "bson_shared" if self.options.shared else "bson_static"
        self.cpp_info.components["bson"].set_property("cmake_target_name", "mongo::{}".format(bson_target))
        self.cpp_info.components["bson"].set_property("pkg_config_name", "libbson-1.0" if self.options.shared else "libbson-static-1.0")

        self.cpp_info.components["bson"].names["cmake_find_package"] = bson_target
        self.cpp_info.components["bson"].names["cmake_find_package_multi"] = bson_target

        self.cpp_info.components["bson"].includedirs = [os.path.join("include", "libbson-1.0")]
        self.cpp_info.components["bson"].libs = ["bson-1.0" if self.options.shared else "bson-static-1.0"]
        if not self.options.shared:
            self.cpp_info.components["bson"].defines = ["BSON_STATIC"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["bson"].system_libs = ["m", "pthread", "rt"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["bson"].system_libs = ["ws2_32"]
