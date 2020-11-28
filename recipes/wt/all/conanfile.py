from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil

required_conan_version = ">=1.28.0"

class WtConan(ConanFile):
    name = "wt"
    description = "Wt is a C++ library for developing web applications"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/emweb/wt"
    topics = ("conan", "wt", "web", "webapp")
    license = "GPL-2.0-only"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ssl": [True, False],
        "with_sqlite": [True, False],
        "with_postgres": [True, False],
        "with_mysql": [True, False],
        "with_mssql": [True, False],
        "with_test": [True, False],
        "with_dbo": [True, False],
        "with_opengl": [True, False],
        "with_unwind": [True, False],
        "no_std_locale": [True, False],
        "no_std_wstring": [True, False],
        "multi_threaded": [True, False],
        "connector_http": [True, False],
        "connector_isapi": [True, False],
        "connector_fcgi": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssl": True,
        "with_sqlite": True,
        "with_postgres": True,
        "with_mysql": True,
        "with_mssql": False,
        "with_test": False,
        "with_dbo": True,
        "with_opengl": False,
        "with_unwind": True,
        "no_std_locale": False,
        "no_std_wstring": False,
        "multi_threaded": True,
        "connector_http": True,
        "connector_isapi": True,
        "connector_fcgi": False
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
            del self.options.connector_fcgi
        else:
            del self.options.connector_isapi
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_unwind

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self.options.with_dbo:
            del self.options.with_sqlite
            del self.options.with_postgres
            del self.options.with_mysql
            del self.options.with_mssql
        self._strict_options_requirements()

    def _strict_options_requirements(self):
        self.options["boost"].header_only = False
        for boost_comp in self._required_boost_components:
            setattr(self.options["boost"], "without_{}".format(boost_comp), False)

    @property
    def _required_boost_components(self):
        return ["program_options", "filesystem", "thread"]

    def requirements(self):
        self.requires("boost/1.74.0")
        if self.options.connector_http:
            self.requires("zlib/1.2.11")
        if self.options.with_ssl:
            self.requires("openssl/1.1.1h")
        if self.options.get_safe("with_sqlite"):
            self.requires("sqlite3/3.32.3")
        if self.options.get_safe("with_mysql"):
            self.requires("libmysqlclient/8.0.17")
        if self.options.get_safe("with_postgres"):
            self.requires("libpq/12.2")
        if self.options.get_safe("with_mssql") and self.settings.os != "Windows":
            self.requires("odbc/2.3.7")
        if self.options.get_safe("with_unwind"):
            self.requires("libunwind/1.5.0")

    # TODO: move this logic in method which might be implemented by https://github.com/conan-io/conan/issues/7591
    def _validate_dependency_graph(self):
        miss_boost_required_comp = any(getattr(self.options["boost"], "without_{}".format(boost_comp), True) for boost_comp in self._required_boost_components)
        if self.options["boost"].header_only or miss_boost_required_comp:
            raise ConanInvalidConfiguration("Wt requires these boost components: {}".format(", ".join(self._required_boost_components)))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CONFIGDIR"] = os.path.join(self.package_folder, "bin")
        self._cmake.definitions["SHARED_LIBS"] = self.options.shared
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["ENABLE_SSL"] = self.options.with_ssl
        self._cmake.definitions["ENABLE_HARU"] = False
        self._cmake.definitions["ENABLE_PANGO"] = False
        self._cmake.definitions["ENABLE_SQLITE"] = self.options.get_safe("with_sqlite", False)
        self._cmake.definitions["ENABLE_POSTGRES"] = self.options.get_safe("with_postgres", False)
        self._cmake.definitions["ENABLE_FIREBIRD"] = False
        self._cmake.definitions["ENABLE_MYSQL"] = self.options.get_safe("with_mysql", False)
        self._cmake.definitions["ENABLE_MSSQLSERVER"] = self.options.get_safe("with_mssql", False)
        self._cmake.definitions["ENABLE_QT4"] = False
        self._cmake.definitions["ENABLE_QT5"] = False
        self._cmake.definitions["ENABLE_LIBWTTEST"] = self.options.with_test
        self._cmake.definitions["ENABLE_LIBWTDBO"] = self.options.with_dbo
        self._cmake.definitions["ENABLE_OPENGL"] = self.options.with_opengl
        self._cmake.definitions["ENABLE_UNWIND"] = self.options.get_safe("with_unwind", False)
        self._cmake.definitions["WT_NO_STD_LOCALE"] = self.options.no_std_locale
        self._cmake.definitions["WT_NO_STD_WSTRING"] = self.options.no_std_wstring
        self._cmake.definitions["MULTI_THREADED"] = self.options.multi_threaded
        self._cmake.definitions["USE_SYSTEM_SQLITE3"] = True
        self._cmake.definitions["DEBUG"] = self.settings.build_type == "Debug"
        self._cmake.definitions["CONNECTOR_HTTP"] = self.options.connector_http
        self._cmake.definitions["BOOST_DYNAMIC"] = self.options["boost"].shared

        def _gather_libs(p):
            libs = self.deps_cpp_info[p].libs + self.deps_cpp_info[p].system_libs
            if not getattr(self.options[p], "shared", False):
                for dep in self.deps_cpp_info[p].public_deps:
                    for l in _gather_libs(dep):
                        if not l in libs:
                            libs.append(l)
            return libs

        if self.options.with_ssl:
            self._cmake.definitions["OPENSSL_PREFIX"] = self.deps_cpp_info["openssl"].rootpath
            self._cmake.definitions["OPENSSL_LIBRARIES"] = ";".join(_gather_libs("openssl"))
            self._cmake.definitions["OPENSSL_INCLUDE_DIR"] = ";".join(self.deps_cpp_info["openssl"].include_paths)
            self._cmake.definitions["OPENSSL_FOUND"] = True
        if self.options.get_safe("with_mysql"):
            self._cmake.definitions["MYSQL_LIBRARIES"] = ";".join(_gather_libs("libmysqlclient"))
            self._cmake.definitions["MYSQL_INCLUDE"] = ";".join(self.deps_cpp_info["libmysqlclient"].include_paths)
            self._cmake.definitions["MYSQL_DEFINITIONS"] = ";".join("-D%s" % d for d in self.deps_cpp_info["libmysqlclient"].defines)
            self._cmake.definitions["MYSQL_FOUND"] = True
        if self.options.get_safe("with_postgres"):
            self._cmake.definitions["POSTGRES_LIBRARIES"] = ";".join(_gather_libs("libpq"))
            self._cmake.definitions["POSTGRES_INCLUDE"] = ";".join(self.deps_cpp_info["libpq"].include_paths)
            self._cmake.definitions["POSTGRES_FOUND"] = True
        if self.options.get_safe("with_mssql") and self.settings.os != "Windows":
            self._cmake.definitions["ODBC_LIBRARIES"] = ";".join(_gather_libs("odbc"))
            self._cmake.definitions["ODBC_INCLUDE"] = ";".join(self.deps_cpp_info["odbc"].include_paths)
            self._cmake.definitions["ODBC_FOUND"] = True
        if self.settings.os == "Windows":
            self._cmake.definitions["CONNECTOR_FCGI"] = False
            self._cmake.definitions["CONNECTOR_ISAPI"] = self.options.connector_isapi
        else:
            self._cmake.definitions["CONNECTOR_FCGI"] = self.options.connector_fcgi
            self._cmake.definitions["CONNECTOR_ISAPI"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._validate_dependency_graph()
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "find_package(OpenSSL)", "#find_package(OpenSSL)")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "INCLUDE(cmake/WtFindMysql.txt)", "#INCLUDE(cmake/WtFindMysql.txt)")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "INCLUDE(cmake/WtFindPostgresql.txt)", "#INCLUDE(cmake/WtFindPostgresql.txt)")
        if self.settings.os != "Windows":
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "INCLUDE(cmake/WtFindOdbc.txt)", "#INCLUDE(cmake/WtFindOdbc.txt)")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        shutil.move(os.path.join(self.package_folder, "share", "Wt"), os.path.join(self.package_folder, "bin"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "var"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "wt"
        self.cpp_info.filenames["cmake_find_package_multi"] = "wt"
        self.cpp_info.names["cmake_find_package"] = "Wt"
        self.cpp_info.names["cmake_find_package_multi"] = "Wt"
        # wt
        self.cpp_info.components["wtmain"].names["cmake_find_package"] = "Wt"
        self.cpp_info.components["wtmain"].names["cmake_find_package_multi"] = "Wt"
        self.cpp_info.components["wtmain"].libs = [self._lib_name("wt")]
        if self.settings.os == "Linux":
            self.cpp_info.components["wtmain"].system_libs = ["m", "rt"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["wtmain"].system_libs = ["ws2_32", "mswsock", "winmm"]
        self.cpp_info.components["wtmain"].requires = ["boost::boost"]
        if self.options.with_ssl:
            self.cpp_info.components["wtmain"].requires.append("openssl::openssl")
        if self.options.get_safe("with_unwind"):
            self.cpp_info.components["wtmain"].requires.append("libunwind::libunwind")
        # wttest
        if self.options.with_test:
            self.cpp_info.components["wttest"].names["cmake_find_package"] = "Test"
            self.cpp_info.components["wttest"].names["cmake_find_package_multi"] = "Test"
            self.cpp_info.components["wttest"].libs = [self._lib_name("wttest")]
            self.cpp_info.components["wttest"].requires = ["wtmain"]
        # wthttp
        if self.options.connector_http:
            self.cpp_info.components["wthttp"].names["cmake_find_package"] = "HTTP"
            self.cpp_info.components["wthttp"].names["cmake_find_package_multi"] = "HTTP"
            self.cpp_info.components["wthttp"].libs = [self._lib_name("wthttp")]
            self.cpp_info.components["wthttp"].requires = ["wtmain", "boost::boost", "zlib::zlib"]
            if self.options.with_ssl:
                self.cpp_info.components["wthttp"].requires.append("openssl::openssl")
        # wtisapi
        if self.options.get_safe("connector_isapi"):
            self.cpp_info.components["wtisapi"].names["cmake_find_package"] = "Isapi"
            self.cpp_info.components["wtisapi"].names["cmake_find_package_multi"] = "Isapi"
            self.cpp_info.components["wtisapi"].libs = [self._lib_name("wtisapi")]
            self.cpp_info.components["wtisapi"].requires = ["wtmain"]
        # wtfcgi
        if self.options.get_safe("connector_fcgi"):
            self.cpp_info.components["wtfcgi"].names["cmake_find_package"] = "FCGI"
            self.cpp_info.components["wtfcgi"].names["cmake_find_package_multi"] = "FCGI"
            self.cpp_info.components["wtfcgi"].libs = [self._lib_name("wtfcgi")]
            self.cpp_info.components["wtfcgi"].requires = ["wtmain"]
            if self.options.with_ssl:
                self.cpp_info.components["wtfcgi"].requires.append("openssl::openssl")
        # wtdbo
        if self.options.with_dbo:
            self.cpp_info.components["wtdbo"].names["cmake_find_package"] = "Dbo"
            self.cpp_info.components["wtdbo"].names["cmake_find_package_multi"] = "Dbo"
            self.cpp_info.components["wtdbo"].libs = [self._lib_name("wtdbo")]
            if self.options.get_safe("with_unwind"):
                self.cpp_info.components["wtdbo"].requires.append("libunwind::libunwind")
        # wtdbosqlite3
        if self.options.get_safe("with_sqlite"):
            self.cpp_info.components["wtdbosqlite3"].names["cmake_find_package"] = "DboSqlite3"
            self.cpp_info.components["wtdbosqlite3"].names["cmake_find_package_multi"] = "DboSqlite3"
            self.cpp_info.components["wtdbosqlite3"].libs = [self._lib_name("wtdbosqlite3")]
            self.cpp_info.components["wtdbosqlite3"].requires = ["wtdbo", "sqlite3::sqlite3"]
            if self.settings.os == "Linux":
                self.cpp_info.components["wtdbosqlite3"].system_libs = ["m"]
        # wtdbopostgres
        if self.options.get_safe("with_postgres"):
            self.cpp_info.components["wtdbopostgres"].names["cmake_find_package"] = "DboPostgres"
            self.cpp_info.components["wtdbopostgres"].names["cmake_find_package_multi"] = "DboPostgres"
            self.cpp_info.components["wtdbopostgres"].libs = [self._lib_name("wtdbopostgres")]
            self.cpp_info.components["wtdbopostgres"].requires = ["wtdbo", "libpq::libpq"]
        # wtdbomysql
        if self.options.get_safe("with_mysql"):
            self.cpp_info.components["wtdbomysql"].names["cmake_find_package"] = "DboMySQL"
            self.cpp_info.components["wtdbomysql"].names["cmake_find_package_multi"] = "DboMySQL"
            self.cpp_info.components["wtdbomysql"].libs = [self._lib_name("wtdbomysql")]
            self.cpp_info.components["wtdbomysql"].requires = ["wtdbo", "libmysqlclient::libmysqlclient"]
        # wtdbomssqlserver
        if self.options.get_safe("with_mssql"):
            self.cpp_info.components["wtdbomssqlserver"].names["cmake_find_package"] = "DboMSSQLServer"
            self.cpp_info.components["wtdbomssqlserver"].names["cmake_find_package_multi"] = "DboMSSQLServer"
            self.cpp_info.components["wtdbomssqlserver"].libs = [self._lib_name("wtdbomssqlserver")]
            self.cpp_info.components["wtdbomssqlserver"].requires = ["wtdbo"]
            if self.settings.os == "Windows":
                self.cpp_info.components["wtdbomssqlserver"].system_libs.append("odbc32")
            else:
                self.cpp_info.components["wtdbomssqlserver"].requires.append("odbc::odbc")

    def _lib_name(self, name):
        if self.settings.build_type == "Debug":
            return name + "d"
        return name
