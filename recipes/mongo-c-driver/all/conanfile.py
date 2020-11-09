from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.28.0"

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
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ssl": [False, 'DARWIN', 'WINDOWS', 'OPENSSL', 'LIBRESSL'],
        "with_snappy": [True, False],
        "with_zlib": [True, False],
        "with_zstd": [True, False],
        "with_icu": [True, False]
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssl": 'OPENSSL',
        "with_snappy": True,
        "with_zlib": True,
        "with_zstd": True,
        "with_icu": True
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

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC
        if self.options.with_ssl == "DARWIN" and not tools.is_apple_os(self.settings.os):
            raise ConanInvalidConfiguration("with_ssl=DARWIN only allowed on Apple os family")
        if self.options.with_ssl == "WINDOWS" and self.settings.os != "Windows":
            raise ConanInvalidConfiguration("with_ssl=WINDOWS only allowed on Windows")

    def requirements(self):
        if self.options.with_ssl == 'OPENSSL':
            self.requires("openssl/1.1.1h")
        if self.options.with_ssl == 'LIBRESSL':
            self.output.warn("Can be broken. Prefer OpenSSL instead of LIBRESSL")
            self.requires("libressl/3.2.0")
        if self.options.with_snappy:
            self.requires("snappy/1.1.8")
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.with_zstd:
            self.requires("zstd/1.4.5")
        if self.options.with_icu:
            self.requires("icu/68.1")

    def build_requirements(self):
        if self.options.with_zstd:
            self.build_requires("pkgconf/1.7.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # Fix Snappy
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "libmongoc", "CMakeLists.txt"),
                              "include (FindSnappy)\nif (SNAPPY_INCLUDE_DIRS)",
                              "if(ENABLE_SNAPPY MATCHES \"ON\")\n  find_package(Snappy REQUIRED)")
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "libmongoc", "CMakeLists.txt"),
                              "SNAPPY_LIBRARIES",
                              "Snappy_LIBRARIES")
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "libmongoc", "CMakeLists.txt"),
                              "SNAPPY_INCLUDE_DIRS",
                              "Snappy_INCLUDE_DIRS")

        if self.options.with_ssl == 'LIBRESSL':
            tools.replace_in_file(
                os.path.join(self._source_subfolder, "src", "libmongoc", "CMakeLists.txt"),
                self._libressl_find_pattern,
                self._libressl_replacement_pattern.format(
                    LIBRESSL_INCLUDE_DIRS=self.deps_cpp_info["libressl"].include_paths[0],
                    LIBRESSL_LIBRARY_DIRS=self.deps_cpp_info["libressl"].lib_paths[0]
                ))

    _libressl_find_pattern = '''
   if (ENABLE_SSL STREQUAL LIBRESSL)
      include (FindPkgConfig)
      message ("-- Searching for LibreSSL/libtls")
      pkg_check_modules (LIBRESSL libtls)
      if (LIBRESSL_FOUND)
         message ("--   Found ${LIBRESSL_LIBRARIES}")
         set (SSL_LIBRARIES ${LIBRESSL_LIBRARIES})
         if (LIBRESSL_INCLUDE_DIRS)
           include_directories ("${LIBRESSL_INCLUDE_DIRS}")
         endif ()
         link_directories ("${LIBRESSL_LIBRARY_DIRS}")
         set (LIBRESSL 1)
      else ()
         message ("--   Not found")
      endif ()
   endif ()
'''

    _libressl_replacement_pattern = '''
   if (ENABLE_SSL STREQUAL LIBRESSL)
        message ("--   USE LIBRESSL include: {LIBRESSL_INCLUDE_DIRS}!")
        message ("--   USE LIBRESSL library: {LIBRESSL_LIBRARY_DIRS}!")
        include_directories ("{LIBRESSL_INCLUDE_DIRS}")
        link_directories ("{LIBRESSL_LIBRARY_DIRS}")
        set (LIBRESSL 1)
   endif ()
'''

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CMAKE_INSTALL_SYSTEM_RUNTIME_LIBS_SKIP"] = "TRUE"
        self._cmake.definitions["ENABLE_TESTS"] = "OFF"
        self._cmake.definitions["ENABLE_EXAMPLES"] = "OFF"
        self._cmake.definitions["ENABLE_STATIC"] = "OFF" if self.options.shared else "ON"
        self._cmake.definitions["ENABLE_SSL"] = self.options.with_ssl
        self._cmake.definitions["ENABLE_SNAPPY"] = "ON" if self.options.with_snappy else "OFF"
        self._cmake.definitions["ENABLE_ZLIB"] = "SYSTEM" if self.options.with_zlib else "OFF"
        self._cmake.definitions["ENABLE_ZSTD"] = "ON" if self.options.with_zstd else "OFF"
        self._cmake.definitions["ENABLE_ICU"] = "ON" if self.options.with_icu else "OFF"
        self._cmake.definitions["ENABLE_SHM_COUNTERS"] = "OFF"
        self._cmake.definitions["ENABLE_BSON"] = "ON"
        self._cmake.definitions["ENABLE_MONGOC"] = "ON"
        if self.settings.os == "Windows":
            self._cmake.definitions["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = self.options.shared
        if self.options.with_ssl == 'OPENSSL':
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
        self.cpp_info.filenames["cmake_find_package"] = "mongoc"
        self.cpp_info.filenames["cmake_find_package_multi"] = "mongoc"
        self.cpp_info.names["cmake_find_package"] = "mongo"
        self.cpp_info.names["cmake_find_package_multi"] = "mongo"
        # mongoc
        self.cpp_info.components["mongoc"].names["cmake_find_package"] = "mongoc" if self.options.shared else "mongoc_static"
        self.cpp_info.components["mongoc"].names["cmake_find_package_multi"] = "mongoc" if self.options.shared else "mongoc_static"
        self.cpp_info.components["mongoc"].names["pkg_config"] = "libmongoc-1.0" if self.options.shared else "libmongoc-static-1.0"
        self.cpp_info.components["mongoc"].includedirs = [os.path.join("include", "libmongoc-1.0")]
        self.cpp_info.components["mongoc"].libs = ["mongoc-1.0" if self.options.shared else "mongoc-static-1.0"]
        if not self.options.shared:
            self.cpp_info.components["mongoc"].defines = ["MONGOC_STATIC"]
        self.cpp_info.components["mongoc"].requires = ["bson"]
        if self.settings.os == "Windows":
            self.cpp_info.components["mongoc"].system_libs.append("ws2_32")
        if self.options.with_ssl == "DARWIN":
            self.cpp_info.components["mongoc"].frameworks.extend(["CoreFoundation", "Security"])
        elif self.options.with_ssl == "WINDOWS":
            self.cpp_info.components["mongoc"].system_libs.extend(["secur32", "crypt32", "bcrypt"])
        elif self.options.with_ssl == "OPENSSL":
            self.cpp_info.components["mongoc"].requires.append("openssl::openssl")
        elif self.options.with_ssl == "LIBRESSL":
            self.cpp_info.components["mongoc"].requires.append("libressl::libressl")
        if self.options.with_snappy:
            self.cpp_info.components["mongoc"].requires.append("snappy::snappy")
        if self.options.with_zlib:
            self.cpp_info.components["mongoc"].requires.append("zlib::zlib")
        if self.options.with_zstd:
            self.cpp_info.components["mongoc"].requires.append("zstd::zstd")
        if self.options.with_icu:
            self.cpp_info.components["mongoc"].requires.append("icu::icu")
        # bson
        self.cpp_info.components["bson"].names["cmake_find_package"] = "bson" if self.options.shared else "bson_static"
        self.cpp_info.components["bson"].names["cmake_find_package_multi"] = "bson" if self.options.shared else "bson_static"
        self.cpp_info.components["bson"].names["pkg_config"] = "libbson-1.0" if self.options.shared else "libbson-static-1.0"
        self.cpp_info.components["bson"].includedirs = [os.path.join("include", "libbson-1.0")]
        self.cpp_info.components["bson"].libs = ["bson-1.0" if self.options.shared else "bson-static-1.0"]
        if not self.options.shared:
            self.cpp_info.components["bson"].defines = ["BSON_STATIC"]
        if self.settings.os == "Linux":
            self.cpp_info.components["bson"].system_libs = ["m", "pthread", "rt"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["bson"].system_libs = ["ws2_32"]
