from conans import ConanFile, CMake, tools
import os


class MongoCDriverConan(ConanFile):
    name = "mongo-c-driver"
    license = "Apache License 2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://mongoc.org/"
    description = "A Cross Platform MongoDB Client Library for C"
    topics = ("conan", "libbson", "libmongoc", "mongo", "mongodb", "database", "db")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "ssl_provider": ['DARWIN', 'WINDOWS', 'OPENSSL', 'LIBRESSL', 'OFF'],
        "zlib": ['SYSTEM', 'BUNDLED', 'OFF']
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "ssl_provider": 'OPENSSL',
        "zlib": 'BUNDLED'
    }
    generators = "cmake"
    no_copy_source = True
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CMAKE_INSTALL_SYSTEM_RUNTIME_LIBS_SKIP"] = "TRUE"
        self._cmake.definitions["ENABLE_TESTS"] = "OFF"
        self._cmake.definitions["ENABLE_EXAMPLES"] = "OFF"
        # todo: apply patch https://github.com/microsoft/vcpkg/blob/master/ports/mongo-c-driver/disable-static-when-dynamic-build.patch
        self._cmake.definitions["ENABLE_STATIC"] = "OFF" if self.options.shared else "ON"
        self._cmake.definitions["ENABLE_SSL"] = self.options.ssl_provider
        self._cmake.definitions["ENABLE_ZLIB"] = self.options.zlib
        self._cmake.definitions["ENABLE_SHM_COUNTERS"] = "OFF"
        if self.options.zlib == 'SYSTEM':
            self._cmake.definitions["ZLIB_ROOT"] = self.deps_cpp_info["zlib"].rootpath
        if self.options.ssl_provider == 'OPENSSL':
            self._cmake.definitions["OPENSSL_ROOT_DIR"] = self.deps_cpp_info["openssl"].rootpath

        self._cmake.configure(
            source_folder=self._source_subfolder,
            build_folder=self._build_subfolder
        )

        return self._cmake

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "{name}-{version}".format(
            name=self.name,
            version=self.version
        )
        os.rename(extracted_dir, self._source_subfolder)
        # todo: fix it https://github.com/bincrafters/community/issues/995
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "src", "libmongoc", "CMakeLists.txt"),
            "add_executable (mongoc-stat ${PROJECT_SOURCE_DIR}/../../src/tools/mongoc-stat.c)",
            "# add_executable (mongoc-stat ${PROJECT_SOURCE_DIR}/../../src/tools/mongoc-stat.c)")
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "src", "libmongoc", "CMakeLists.txt"),
            "target_link_libraries (mongoc-stat mongoc_shared ${LIBRARIES})",
            "# target_link_libraries (mongoc-stat mongoc_shared ${LIBRARIES})")
        if self.options.ssl_provider == 'LIBRESSL':
            tools.replace_in_file(
                os.path.join(self._source_subfolder, "src", "libmongoc", "CMakeLists.txt"),
                self._libressl_find_pattern,
                self._libressl_replacement_pattern.format(
                    LIBRESSL_INCLUDE_DIRS=self.deps_cpp_info["libressl"].include_paths[0],
                    LIBRESSL_LIBRARY_DIRS=self.deps_cpp_info["libressl"].lib_paths[0]
                ))

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.options.shared:
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.ssl_provider == 'OPENSSL':
            self.requires("openssl/1.1.1g")
        if self.options.ssl_provider == 'LIBRESSL':
            self.output.warn("Can be broken. Prefer OpenSSL instead of LIBRESSL")
            self.requires("libressl/3.2.0")
        if self.options.zlib == 'SYSTEM':
            self.requires("zlib/1.2.11")
            if tools.os_info.is_windows:
                self.output.warn("Usage zlib provided by conan on Windows can be broken")

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="THIRD_PARTY_NOTICES", dst="licenses", src=self._source_subfolder)

        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["bson-1.0", "mongoc-1.0"] if self.options.shared else \
            ["bson-static-1.0", "mongoc-static-1.0"]
        self.cpp_info.includedirs.append(os.path.join("include", "libmongoc-1.0"))
        self.cpp_info.includedirs.append(os.path.join("include", "libbson-1.0"))

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
