from conans import ConanFile, CMake, tools
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
    generators = "cmake"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ssl": [False, 'DARWIN', 'WINDOWS', 'OPENSSL', 'LIBRESSL'],
        "with_zlib": [False, 'SYSTEM', 'BUNDLED']
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssl": 'OPENSSL',
        "with_zlib": 'BUNDLED'
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

    def requirements(self):
        if self.options.with_ssl == 'OPENSSL':
            self.requires("openssl/1.1.1h")
        if self.options.with_ssl == 'LIBRESSL':
            self.output.warn("Can be broken. Prefer OpenSSL instead of LIBRESSL")
            self.requires("libressl/3.2.0")
        if self.options.with_zlib == 'SYSTEM':
            self.requires("zlib/1.2.11")
            if tools.os_info.is_windows:
                self.output.warn("Usage zlib provided by conan on Windows can be broken")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
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
        self._cmake.definitions["ENABLE_SNAPPY"] = "OFF"
        self._cmake.definitions["ENABLE_ZLIB"] = self.options.with_zlib
        self._cmake.definitions["ENABLE_ZSTD"] = "OFF"
        self._cmake.definitions["ENABLE_SHM_COUNTERS"] = "OFF"
        self._cmake.definitions["ENABLE_BSON"] = "ON"
        self._cmake.definitions["ENABLE_MONGOC"] = "ON"
        if self.settings.os == "Windows":
            self._cmake.definitions["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = self.options.shared
        if self.options.with_zlib == 'SYSTEM':
            self._cmake.definitions["ZLIB_ROOT"] = self.deps_cpp_info["zlib"].rootpath
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
        if self.options.with_ssl == "OPENSSL":
            self.cpp_info.components["mongoc"].requires.append("openssl::openssl")
        elif self.options.with_ssl == "LIBRESSL":
            self.cpp_info.components["mongoc"].requires.append("libressl::libressl")
        if self.options.with_zlib == "SYSTEM":
            self.cpp_info.components["mongoc"].requires.append("zlib::zlib")
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
