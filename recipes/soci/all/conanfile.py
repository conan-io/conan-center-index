import os
import copy
from collections import namedtuple
from conans import ConanFile, CMake, tools

class SociConan(ConanFile):
    name = "soci"
    settings = "os", "arch", "compiler", "build_type"
    description = "SOCI - The C++ Database Access Library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://soci.sourceforge.net/"
    license = "BSL-1.0"
    generators = "cmake"
    topics = ("conan", "soci", "database")
    exports_sources=["CMakeLists.txt", "cmake/SOCI-override.cmake"]

    backends = [
#     "db2",
      "empty",
#     "firebird",
      "mysql",
      "odbc",
#     "oracle",
      "postgresql",
      "sqlite3"
    ]

    options = {
        "shared": [True, False],
        "with_boost": [True, False],
        "with_all_backends": [True, False]
    }
    options.update({"with_backend_%s" % backend: [True, False] for backend in backends})

    default_options = {
        "shared": True,
        "with_boost": False,
        "with_all_backends": True
    }

    default_options.update({"with_backend_%s" % backend: None for backend in backends})


    short_paths = True
    no_copy_source = True
      
    def _with_backend(self, with_backend):
      return with_backend == True or with_backend == 'None' and self.options.with_all_backends

    def requirements(self):
        if self.settings.os == "Windows" and self.options.with_backend_odbc == 'None':
            self.options.with_backend_odbc = False
       
        if self._with_backend(self.options.with_backend_sqlite3):
            self.requires("sqlite3/3.31.1")

        if self._with_backend(self.options.with_backend_mysql):
            self.requires("libmysqlclient/8.0.17")
            self.requires("openssl/1.1.1d")

        if self._with_backend(self.options.with_backend_odbc):
            self.requires("odbc/2.3.7")
            if self.options["odbc"].with_libiconv:
                self.requires("libiconv/1.15")

        if self._with_backend(self.options.with_backend_postgresql):
            self.requires("libpq/12.2")

        if self.options.with_boost:
            self.requires("boost/1.73.0")

    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        url = self.conan_data["sources"][self.version]["url"]
        archive_name = os.path.basename(url)
        archive_name = os.path.splitext(archive_name)[0]
        os.rename("soci-%s" % archive_name, self._source_subfolder)
        
    def _dependency(self, name):
        def find_lib_path(name, lib):
            lib_filename = (
              '' if self.settings.os == "Windows" else 'lib'
            ) + lib + (
              '.lib' if self.settings.os == "Windows" else '.so' if self.options[name].shared else '.a'
            )

            for path in self.deps_cpp_info[name].lib_paths:
                full_path = os.path.join(
                  path,
                  lib_filename
                )
                if os.path.isfile(full_path):
                    return full_path
            print('{} not found in {}'.format(lib_filename, self.deps_cpp_info[name].lib_paths))
            return None

        libs = [find_lib_path(name, lib) for lib in self.deps_cpp_info[name].libs]

        return namedtuple('Dependency', ['root', 'libs'])(
          root          = self.deps_cpp_info[name].rootpath,
          libs          = libs
        )

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["SOCI_SHARED"] = self.options.shared
        cmake.definitions["SOCI_STATIC"] = not self.options.shared
        cmake.definitions["SOCI_TESTS"] = False

        print("self.settings.compiler.cppstd = {}".format(self.settings.compiler.cppstd))
        if self.settings.compiler.cppstd != 'None':
            cmake.definitions["CMAKE_CXX_STANDARD"] = self.settings.compiler.cppstd

        cmake.definitions["WITH_EMPTY"] = self._with_backend(self.options.with_backend_empty)

        if self._with_backend(self.options.with_backend_sqlite3):
            sqlite3 = self._dependency('sqlite3')
            cmake.definitions["WITH_SQLITE3"] = "ON"
            cmake.definitions["SQLITE_ROOT_DIR"] = sqlite3.root

        cmake.definitions["WITH_MYSQL"] = self.options.with_backend_mysql
        if self.options.with_backend_mysql:
            mysql = self._dependency('libmysqlclient')
            os.environ["MYSQL_DIR"] = mysql.root  # move this to a `tools.environment_append` context (or a cmake variable)
            cmake.definitions["MYSQL_LIBRARIES"] = ";".join(self.deps_cpp_info["libmysqlclient"].libs)

        if self._with_backend(self.options.with_backend_odbc):
            odbc = self._dependency('odbc')
            cmake.definitions["WITH_ODBC"] = "ON"
            cmake.definitions["ODBC_INCLUDE_DIR"] = ";".join(self.deps_cpp_info["odbc"].include_paths)
            if self.settings.os == 'Windows':
              cmake.definitions["ODBC_LIBRARY"] = ";".join(seld.deps_cpp_info["odb"].libs)
            else:
              cmake.definitions["SOCI_ODBC_DO_NOT_TEST"] = True
              cmake.definitions["ODBC_LIBRARY"] = ";".join(seld.deps_cpp_info["odb"].libs)


        if self._with_backend(self.options.with_backend_postgresql):
            postgresql = self._dependency('libpq')
            cmake.definitions["WITH_POSTGRESQL"] = True
            os.environ["POSTGRESQL_ROOT"] = self.deps_cpp_info["libpq"].rootpath

        #cmake.configure(source_folder=self._source_subfolder)
        cmake.configure()
        cmake.verbose = True
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package_info(self):
        self.cpp_info.build_modules.append('cmake/SOCI-override.cmake')
        self.cpp_info.builddirs.append('cmake')
        
        if self.options.with_boost:
          self.cpp_info.defines.append('-DSOCI_USE_BOOST')


    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy('LICENSE_1_0.txt', dst='licenses', src=self._source_subfolder)
        self.copy('cmake/SOCI-override.cmake')
