from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class SociConan(ConanFile):
    name = "soci"
    settings = "os", "arch", "compiler", "build_type"
    description = "SOCI - The C++ Database Access Library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://soci.sourceforge.net/"
    license = "BSL-1.0"
    generators = "cmake", "cmake_find_package"
    topics = ("conan", "soci", "database")
    exports_sources = "CMakeLists.txt", "patches/**"

    short_paths = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    _cmake = None

    _backend_default_option = {
        "empty": True,
        "mysql": True,
        "odbc": True,
        "postgresql": True,
        "sqlite3": True,
        "db2": False,
        "firebird": False,
        "oracle": False,
    }

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_boost": [True, False],
    }
    options.update({"with_backend_{}".format(backend): [True, False] for backend in _backend_default_option.keys()})

    default_options = {
        "shared": False,
        "fPIC": True,
        "with_boost": False,
    }
    default_options.update({"with_backend_{}".format(backend): default for backend, default in _backend_default_option.items()})

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        if self.options.with_backend_sqlite3:
            self.requires("sqlite3/3.31.1")

        if self.options.with_backend_mysql:
            self.requires("libmysqlclient/8.0.17")

        if self.options.with_backend_odbc:
            self.requires("odbc/2.3.7")
            if self.options["odbc"].with_libiconv:
                self.requires("libiconv/1.15")

        if self.options.with_backend_postgresql:
            self.requires("libpq/11.5")

        if self.options.with_backend_db2:
            # FIXME: add db2 support
            raise ConanInvalidConfiguration("db2 is not (yet) available on CCI")
            self.requires("db2/x.y.z")

        if self.options.with_backend_firebird:
            # FIXME: add firebird support
            raise ConanInvalidConfiguration("firebird is not (yet) available on CCI")
            self.requires("firebird/x.y.z")

        if self.options.with_backend_oracle:
            # FIXME: add oracle support
            raise ConanInvalidConfiguration("oracle is not (yet) available on CCI")
            self.requires("oracle/x.y.z")

        if self.options.with_boost:
            self.requires("boost/1.73.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("soci-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        self._cmake.definitions["BINDIR"] = os.path.join(self.package_folder, "bin")
        self._cmake.definitions["LIBDIR"] = os.path.join(self.package_folder, "lib")
        self._cmake.definitions["LIB_SUFFIX"] = ""

        self._cmake.definitions["SOCI_SHARED"] = self.options.shared
        self._cmake.definitions["SOCI_STATIC"] = not self.options.shared
        self._cmake.definitions["SOCI_TESTS"] = False

        self._cmake.definitions["WITH_BOOST"] = self.options.with_boost
        self._cmake.definitions["SOCI_EMPTY"] = self.options.with_backend_empty
        self._cmake.definitions["WITH_SQLITE3"] = self.options.with_backend_sqlite3
        self._cmake.definitions["WITH_MYSQL"] = self.options.with_backend_mysql
        self._cmake.definitions["WITH_ODBC"] = self.options.with_backend_odbc
        self._cmake.definitions["WITH_POSTGRESQL"] = self.options.with_backend_postgresql

        self._cmake.definitions["WITH_DB2"] = self.options.with_backend_db2
        self._cmake.definitions["WITH_FIREBIRD"] = self.options.with_backend_firebird
        self._cmake.definitions["WITH_ORACLE"] = self.options.with_backend_oracle

        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        if self.options.with_backend_sqlite3:
            tools.replace_in_file("FindSQLite3.cmake", "SQLite3_FOUND", "SQLITE3_FOUND")
            tools.replace_in_file("FindSQLite3.cmake", "SQLite3_INCLUDE_DIRS", "SQLITE3_INCLUDE_DIRS")
            tools.replace_in_file("FindSQLite3.cmake", "SQLite3_LIBRARIES", "SQLITE3_LIBRARIES")
        if self.options.with_backend_mysql:
            os.rename("Findlibmysqlclient.cmake", "FindMySQL.cmake")
            tools.replace_in_file("FindMySQL.cmake", "libmysqlclient_FOUND", "MYSQL_FOUND")
            tools.replace_in_file("FindMySQL.cmake", "libmysqlclient_INCLUDE_DIRS", "MYSQL_INCLUDE_DIRS")
            tools.replace_in_file("FindMySQL.cmake", "libmysqlclient_LIBRARIES", "MYSQL_LIBRARIES")
        if self.options.with_backend_postgresql:
            tools.replace_in_file("FindPostgreSQL.cmake", "PostgreSQL_FOUND", "POSTGRESQL_FOUND")
            tools.replace_in_file("FindPostgreSQL.cmake", "PostgreSQL_INCLUDE_DIRS", "POSTGRESQL_INCLUDE_DIRS")
            tools.replace_in_file("FindPostgreSQL.cmake", "PostgreSQL_LIBRARIES", "POSTGRESQL_LIBRARIES")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE_1_0.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "cmake"))

    def _construct_library_name(self, name):
        if self.settings.os == "Windows":
            abi_version = tools.Version(self.version)
            name = "lib{name}_{major}_{minor}".format(
                name = name,
                major = abi_version.major,
                minor = abi_version.minor
            )
        return name

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "SOCI"
        self.cpp_info.names["cmake_find_package_multi"] = "SOCI"

        self.cpp_info.components["core"].libs = [self._construct_library_name("soci_core")]
        if self.options.with_boost:
            self.cpp_info.components["core"].defines.append("SOCI_USE_BOOST")
            self.cpp_info.components["core"].requires.append("boost::boost")
        if self.settings.os == "Linux":
            self.cpp_info.components["core"].system_libs.extend(["dl", "m", "pthread"])

        if self.options.with_backend_empty:
            self.cpp_info.components["empty"].libs = [self._construct_library_name("soci_empty")]
            self.cpp_info.components["empty"].requires = ["core"]

        if self.options.with_backend_sqlite3:
            self.cpp_info.components["sqlite3"].libs = [self._construct_library_name("soci_sqlite3")]
            self.cpp_info.components["sqlite3"].requires = ["core", "sqlite3::sqlite3"]

        if self.options.with_backend_mysql:
            self.cpp_info.components["mysql"].libs = [self._construct_library_name("soci_mysql")]
            self.cpp_info.components["mysql"].requires = ["core", "libmysqlclient::libmysqlclient"]

        if self.options.with_backend_odbc:
            self.cpp_info.components["odbc"].libs = [self._construct_library_name("soci_odbc")]
            self.cpp_info.components["odbc"].requires = ["core", "odbc::odbc"]

        if self.options.with_backend_postgresql:
            self.cpp_info.components["postgresql"].libs = [self._construct_library_name("soci_postgresql")]
            self.cpp_info.components["postgresql"].requires = ["core", "libpq::libpq"]
