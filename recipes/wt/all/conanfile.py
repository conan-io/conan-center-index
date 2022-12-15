from conan import ConanFile
from conan.tools.scm import Version
from conan.tools import files
from conan.tools.cmake import CMakeToolchain, CMake, CMakeDeps, cmake_layout
from conan.errors import ConanInvalidConfiguration
import os
import shutil

required_conan_version = ">=1.46.0"


class WtConan(ConanFile):
    name = "wt"
    description = "Wt is a C++ library for developing web applications"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/emweb/wt"
    topics = ("wt", "web", "webapp")
    license = "GPL-2.0-only"

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
        "connector_fcgi": [True, False],
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
        "connector_fcgi": False,
    }


    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

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
        if Version(self.version) >= "4.6.0":
            self.requires("boost/1.79.0")
        else:
            self.requires("boost/1.76.0")
        if self.options.connector_http:
            self.requires("zlib/1.2.12")
        if self.options.with_ssl:
            self.requires("openssl/1.1.1q")
        if self.options.get_safe("with_sqlite"):
            self.requires("sqlite3/3.39.1")
        if self.options.get_safe("with_mysql"):
            self.requires("libmysqlclient/8.0.29")
        if self.options.get_safe("with_postgres"):
            self.requires("libpq/14.2")
        if self.options.get_safe("with_mssql") and self.settings.os != "Windows":
            self.requires("odbc/2.3.9")
        if self.options.get_safe("with_unwind"):
            self.requires("libunwind/1.6.2")

    def validate(self):
        miss_boost_required_comp = any(getattr(self.options["boost"], "without_{}".format(boost_comp), True) for boost_comp in self._required_boost_components)
        if self.options["boost"].header_only or miss_boost_required_comp:
            raise ConanInvalidConfiguration("Wt requires these boost components: {}".format(", ".join(self._required_boost_components)))

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            files.patch(**patch)

        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        files.replace_in_file(self, cmakelists, "find_package(OpenSSL)", "#find_package(OpenSSL)")
        files.replace_in_file(self, cmakelists, "INCLUDE(cmake/WtFindMysql.txt)", "#INCLUDE(cmake/WtFindMysql.txt)")
        files.replace_in_file(self, cmakelists, "INCLUDE(cmake/WtFindPostgresql.txt)", "#INCLUDE(cmake/WtFindPostgresql.txt)")
        if self.settings.os != "Windows":
            files.replace_in_file(self, cmakelists, "INCLUDE(cmake/WtFindOdbc.txt)", "#INCLUDE(cmake/WtFindOdbc.txt)")

        # Do not pollute rpath of shared libs of the install tree on macOS please
        files.replace_in_file(
            self,
            cmakelists,
            "IF(APPLE)\n  SET(CMAKE_INSTALL_RPATH \"${CMAKE_INSTALL_PREFIX}/lib\")",
            "if(0)",
        )

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CONFIGDIR"] = os.path.join(self.package_folder, "bin")
        tc.variables["SHARED_LIBS"] = self.options.shared
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_TESTS"] = False
        tc.variables["ENABLE_SSL"] = self.options.with_ssl
        tc.variables["ENABLE_HARU"] = False
        tc.variables["ENABLE_PANGO"] = False
        tc.variables["ENABLE_SQLITE"] = self.options.get_safe("with_sqlite", False)
        tc.variables["ENABLE_POSTGRES"] = self.options.get_safe("with_postgres", False)
        tc.variables["ENABLE_FIREBIRD"] = False
        tc.variables["ENABLE_MYSQL"] = self.options.get_safe("with_mysql", False)
        tc.variables["ENABLE_MSSQLSERVER"] = self.options.get_safe("with_mssql", False)
        tc.variables["ENABLE_QT4"] = False
        tc.variables["ENABLE_QT5"] = False
        tc.variables["ENABLE_LIBWTTEST"] = self.options.with_test
        tc.variables["ENABLE_LIBWTDBO"] = self.options.with_dbo
        tc.variables["ENABLE_OPENGL"] = self.options.with_opengl
        tc.variables["ENABLE_UNWIND"] = self.options.get_safe("with_unwind", False)
        tc.variables["WT_NO_STD_LOCALE"] = self.options.no_std_locale
        tc.variables["WT_NO_STD_WSTRING"] = self.options.no_std_wstring
        tc.variables["MULTI_THREADED"] = self.options.multi_threaded
        tc.variables["USE_SYSTEM_SQLITE3"] = True
        tc.variables["DEBUG"] = self.settings.build_type == "Debug"
        tc.variables["CONNECTOR_HTTP"] = self.options.connector_http
        tc.variables["BOOST_DYNAMIC"] = self.options["boost"].shared

        def _gather_libs(p):
            libs = self.deps_cpp_info[p].libs + self.deps_cpp_info[p].system_libs
            for dep in self.deps_cpp_info[p].public_deps:
                for l in _gather_libs(dep):
                    if not l in libs:
                        libs.append(l)
            return libs

        # FIXME: all this logic coming from upstream custom find module files seems fragile, to improve later !
        #        we can't even inject cmake_find_package generator, it breaks the all upstream logic
        tc.variables["BOOST_PREFIX"] = self.deps_cpp_info["boost"].rootpath
        if self.options.connector_http:
            tc.variables["ZLIB_PREFIX"] = self.deps_cpp_info["zlib"].rootpath
        if self.options.with_ssl:
            tc.variables["SSL_PREFIX"] = self.deps_cpp_info["openssl"].rootpath
            tc.variables["OPENSSL_LIBRARIES"] = ";".join(_gather_libs("openssl"))
            tc.variables["OPENSSL_INCLUDE_DIR"] = ";".join(self.deps_cpp_info["openssl"].include_paths)
            tc.variables["OPENSSL_FOUND"] = True
        if self.options.get_safe("with_sqlite"):
            tc.variables["SQLITE3_PREFIX"] = self.deps_cpp_info["sqlite3"].rootpath
        if self.options.get_safe("with_mysql"):
            tc.variables["MYSQL_PREFIX"] = self.deps_cpp_info["libmysqlclient"].rootpath
            tc.variables["MYSQL_LIBRARIES"] = ";".join(_gather_libs("libmysqlclient"))
            tc.variables["MYSQL_INCLUDE"] = ";".join(self.deps_cpp_info["libmysqlclient"].include_paths)
            tc.variables["MYSQL_DEFINITIONS"] = ";".join("-D%s" % d for d in self.deps_cpp_info["libmysqlclient"].defines)
            tc.variables["MYSQL_FOUND"] = True
        if self.options.get_safe("with_postgres"):
            tc.variables["POSTGRES_PREFIX"] = self.deps_cpp_info["libpq"].rootpath
            tc.variables["POSTGRES_LIBRARIES"] = ";".join(_gather_libs("libpq"))
            tc.variables["POSTGRES_INCLUDE"] = ";".join(self.deps_cpp_info["libpq"].include_paths)
            tc.variables["POSTGRES_FOUND"] = True
        if self.options.get_safe("with_mssql") and self.settings.os != "Windows":
            tc.variables["ODBC_PREFIX"] = self.deps_cpp_info["odbc"].rootpath
            tc.variables["ODBC_LIBRARIES"] = ";".join(_gather_libs("odbc"))
            tc.variables["ODBC_INCLUDE"] = ";".join(self.deps_cpp_info["odbc"].include_paths)
            tc.variables["ODBC_FOUND"] = True
        if self.options.get_safe("with_unwind"):
            tc.variables["UNWIND_PREFIX"] = self.deps_cpp_info["libunwind"].rootpath
        if self.settings.os == "Windows":
            tc.variables["CONNECTOR_FCGI"] = False
            tc.variables["CONNECTOR_ISAPI"] = self.options.connector_isapi
        else:
            tc.variables["CONNECTOR_FCGI"] = self.options.connector_fcgi
            tc.variables["CONNECTOR_ISAPI"] = False
        tc.generate()

        cmake_deps = CMakeDeps(self)
        cmake_deps.generate()

    def layout(self):
        cmake_layout(self, src_folder="source_folder")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        files.copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        shutil.move(os.path.join(self.package_folder, "share", "Wt"), os.path.join(self.package_folder, "bin"))
        files.rmdir(self, os.path.join(self.package_folder, "share"))
        files.rmdir(self, os.path.join(self.package_folder, "var"))
        files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "wt")

        suffix = "d" if self.settings.build_type == "Debug" else ""

        # wt
        self.cpp_info.components["wtmain"].set_property("cmake_target_name", "Wt::Wt")
        self.cpp_info.components["wtmain"].libs = ["wt{}".format(suffix)]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["wtmain"].system_libs = ["m", "rt", "atomic"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["wtmain"].system_libs = ["ws2_32", "mswsock", "winmm"]
        self.cpp_info.components["wtmain"].requires = ["boost::boost"]
        if self.options.with_ssl:
            self.cpp_info.components["wtmain"].requires.append("openssl::openssl")
        if self.options.get_safe("with_unwind"):
            self.cpp_info.components["wtmain"].requires.append("libunwind::libunwind")

        # wttest
        if self.options.with_test:
            self.cpp_info.components["wttest"].set_property("cmake_target_name", "Wt::Test")
            self.cpp_info.components["wttest"].libs = ["wttest{}".format(suffix)]
            self.cpp_info.components["wttest"].requires = ["wtmain"]

        # wthttp
        if self.options.connector_http:
            self.cpp_info.components["wthttp"].set_property("cmake_target_name", "Wt::HTTP")
            self.cpp_info.components["wthttp"].libs = ["wthttp{}".format(suffix)]
            self.cpp_info.components["wthttp"].requires = ["wtmain", "boost::boost", "zlib::zlib"]
            if self.options.with_ssl:
                self.cpp_info.components["wthttp"].requires.append("openssl::openssl")

        # wtisapi
        if self.options.get_safe("connector_isapi"):
            self.cpp_info.components["wtisapi"].set_property("cmake_target_name", "Wt::Isapi")
            self.cpp_info.components["wtisapi"].libs = ["wtisapi{}".format(suffix)]
            self.cpp_info.components["wtisapi"].requires = ["wtmain"]

        # wtfcgi
        if self.options.get_safe("connector_fcgi"):
            self.cpp_info.components["wtfcgi"].set_property("cmake_target_name", "Wt::FCGI")
            self.cpp_info.components["wtfcgi"].libs = ["wtfcgi{}".format(suffix)]
            self.cpp_info.components["wtfcgi"].requires = ["wtmain"]
            if self.options.with_ssl:
                self.cpp_info.components["wtfcgi"].requires.append("openssl::openssl")

        # wtdbo
        if self.options.with_dbo:
            self.cpp_info.components["wtdbo"].set_property("cmake_target_name", "Wt::Dbo")
            self.cpp_info.components["wtdbo"].libs = ["wtdbo{}".format(suffix)]
            if self.options.get_safe("with_unwind"):
                self.cpp_info.components["wtdbo"].requires.append("libunwind::libunwind")

        # wtdbosqlite3
        if self.options.get_safe("with_sqlite"):
            self.cpp_info.components["wtdbosqlite3"].set_property("cmake_target_name", "Wt::DboSqlite3")
            self.cpp_info.components["wtdbosqlite3"].libs = ["wtdbosqlite3{}".format(suffix)]
            self.cpp_info.components["wtdbosqlite3"].requires = ["wtdbo", "sqlite3::sqlite3"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["wtdbosqlite3"].system_libs = ["m"]

        # wtdbopostgres
        if self.options.get_safe("with_postgres"):
            self.cpp_info.components["wtdbopostgres"].set_property("cmake_target_name", "Wt::DboPostgres")
            self.cpp_info.components["wtdbopostgres"].libs = ["wtdbopostgres{}".format(suffix)]
            self.cpp_info.components["wtdbopostgres"].requires = ["wtdbo", "libpq::libpq"]

        # wtdbomysql
        if self.options.get_safe("with_mysql"):
            self.cpp_info.components["wtdbomysql"].set_property("cmake_target_name", "Wt::DboMySQL")
            self.cpp_info.components["wtdbomysql"].libs = ["wtdbomysql{}".format(suffix)]
            self.cpp_info.components["wtdbomysql"].requires = ["wtdbo", "libmysqlclient::libmysqlclient"]

        # wtdbomssqlserver
        if self.options.get_safe("with_mssql"):
            self.cpp_info.components["wtdbomssqlserver"].set_property("cmake_target_name", "Wt::DboMSSQLServer")
            self.cpp_info.components["wtdbomssqlserver"].libs = ["wtdbomssqlserver{}".format(suffix)]
            self.cpp_info.components["wtdbomssqlserver"].requires = ["wtdbo"]
            if self.settings.os == "Windows":
                self.cpp_info.components["wtdbomssqlserver"].system_libs.append("odbc32")
            else:
                self.cpp_info.components["wtdbomssqlserver"].requires.append("odbc::odbc")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "wt"
        self.cpp_info.filenames["cmake_find_package_multi"] = "wt"
        self.cpp_info.names["cmake_find_package"] = "Wt"
        self.cpp_info.names["cmake_find_package_multi"] = "Wt"
        self.cpp_info.components["wtmain"].names["cmake_find_package"] = "Wt"
        self.cpp_info.components["wtmain"].names["cmake_find_package_multi"] = "Wt"
        if self.options.with_test:
            self.cpp_info.components["wttest"].names["cmake_find_package"] = "Test"
            self.cpp_info.components["wttest"].names["cmake_find_package_multi"] = "Test"
        if self.options.connector_http:
            self.cpp_info.components["wthttp"].names["cmake_find_package"] = "HTTP"
            self.cpp_info.components["wthttp"].names["cmake_find_package_multi"] = "HTTP"
        if self.options.get_safe("connector_isapi"):
            self.cpp_info.components["wtisapi"].names["cmake_find_package"] = "Isapi"
            self.cpp_info.components["wtisapi"].names["cmake_find_package_multi"] = "Isapi"
        if self.options.get_safe("connector_fcgi"):
            self.cpp_info.components["wtfcgi"].names["cmake_find_package"] = "FCGI"
            self.cpp_info.components["wtfcgi"].names["cmake_find_package_multi"] = "FCGI"
        if self.options.with_dbo:
            self.cpp_info.components["wtdbo"].names["cmake_find_package"] = "Dbo"
            self.cpp_info.components["wtdbo"].names["cmake_find_package_multi"] = "Dbo"
        if self.options.get_safe("with_sqlite"):
            self.cpp_info.components["wtdbosqlite3"].names["cmake_find_package"] = "DboSqlite3"
            self.cpp_info.components["wtdbosqlite3"].names["cmake_find_package_multi"] = "DboSqlite3"
        if self.options.get_safe("with_postgres"):
            self.cpp_info.components["wtdbopostgres"].names["cmake_find_package"] = "DboPostgres"
            self.cpp_info.components["wtdbopostgres"].names["cmake_find_package_multi"] = "DboPostgres"
        if self.options.get_safe("with_mysql"):
            self.cpp_info.components["wtdbomysql"].names["cmake_find_package"] = "DboMySQL"
            self.cpp_info.components["wtdbomysql"].names["cmake_find_package_multi"] = "DboMySQL"
        if self.options.get_safe("with_mssql"):
            self.cpp_info.components["wtdbomssqlserver"].names["cmake_find_package"] = "DboMSSQLServer"
            self.cpp_info.components["wtdbomssqlserver"].names["cmake_find_package_multi"] = "DboMSSQLServer"
