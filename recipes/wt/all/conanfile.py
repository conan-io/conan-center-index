from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, replace_in_file
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.microsoft import is_msvc
import os
import shutil

required_conan_version = ">=1.53.0"

class WtConan(ConanFile):
    name = "wt"
    description = "Wt is a C++ library for developing web applications"
    license = "GPL-2.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/emweb/wt"
    topics = ("server", "web", "webapp", "websocket", "cgi", "fastcgi", "orm")
    package_type = "library"
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
        export_conandata_patches(self)

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
            self.options.rm_safe("fPIC")
        if not self.options.with_dbo:
            del self.options.with_sqlite
            del self.options.with_postgres
            del self.options.with_mysql
            del self.options.with_mssql
        self._strict_options_requirements()

    def layout(self):
        cmake_layout(self, src_folder="src")

    def _strict_options_requirements(self):
        self.options["boost"].header_only = False
        for boost_comp in self._required_boost_components:
            setattr(self.options["boost"], f"without_{boost_comp}", False)

    @property
    def _required_boost_components(self):
        return ["program_options", "filesystem", "thread"]

    def requirements(self):
        if Version(self.version) < "4.6.0":
            self.requires("boost/1.76.0")
        elif Version(self.version) < "4.9.0":
            self.requires("boost/1.80.0")
        else:
            self.requires("boost/1.81.0")
        if self.options.connector_http:
            self.requires("zlib/1.2.13")
        if self.options.with_ssl:
            self.requires("openssl/[>=1.1 <4]")
        if self.options.get_safe("with_sqlite"):
            self.requires("sqlite3/3.41.2")
        if self.options.get_safe("with_mysql"):
            self.requires("libmysqlclient/8.0.31", transitive_headers=True, transitive_libs=True)
        if self.options.get_safe("with_postgres"):
            self.requires("libpq/14.7", transitive_headers=True, transitive_libs=True)
        if self.options.get_safe("with_mssql") and self.settings.os != "Windows":
            self.requires("odbc/2.3.11")
        if self.options.get_safe("with_unwind"):
            self.requires("libunwind/1.6.2")

    def validate(self):
        miss_boost_required_comp = any(self.dependencies["boost"].options.get_safe(f"without_{boost_comp}", True)
                                       for boost_comp in self._required_boost_components)
        if self.dependencies["boost"].options.header_only or miss_boost_required_comp:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires non header-only boost with these components: "
                f"{', '.join(self._required_boost_components)}"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _get_library_extension(self, dep):
        if self.dependencies[dep].options.shared:
            if self.settings.os == "Windows" :
                if is_msvc(self):
                    return ".lib"
                else:
                    return ".dll.a"
            elif self.settings.os == "Macos":
                return ".dylib"
            else:
                return ".so"
        else:
            if self.settings.os == "Windows" and is_msvc(self):
                return ".lib"
            else:
                return ".a"

    @property
    def _get_library_prefix(self):
        return "" if self.settings.os == "Windows" else "lib"

    def _cmakify_path_list(self, paths):
        return ";".join(paths).replace("\\", "/")

    def _find_library(self, libname, dep):
        for path in self.dependencies[dep].cpp_info.aggregated_components().libdirs:
            lib_fullpath = os.path.join(path, self._get_library_prefix + libname + self._get_library_extension(dep))
            self.output.info("_find_library : " + str(lib_fullpath))
            if os.path.isfile(lib_fullpath):
                return lib_fullpath
        raise ConanException(f"Library {lib_fullpath} not found")

    def _find_libraries(self, dep):

        return [self._find_library(lib, dep) for lib in self.dependencies[dep].cpp_info.aggregated_components().libs]

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CONFIGDIR"] = os.path.join(self.package_folder, "bin").replace("\\", "/")
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
        tc.variables["BOOST_DYNAMIC"] = self.dependencies["boost"].options.get_safe("shared", False)

        # FIXME: all this logic coming from upstream custom find module files seems fragile, to improve later !
        #        we can't even inject cmake_find_package generator, it breaks the all upstream logic
        tc.variables["BOOST_PREFIX"] = self._cmakify_path_list(self.dependencies["boost"].package_folder)
        if self.options.connector_http:
            tc.variables["ZLIB_PREFIX"] = self._cmakify_path_list(self.dependencies["zlib"].package_folder)
        if self.options.with_ssl:
            tc.variables["SSL_PREFIX"] = self._cmakify_path_list(self.dependencies["openssl"].package_folder)
            tc.variables["OPENSSL_LIBRARIES"] = self._cmakify_path_list(self._find_libraries("openssl"))
            tc.variables["OPENSSL_INCLUDE_DIR"] = self._cmakify_path_list(self.dependencies["openssl"].cpp_info.aggregated_components().includedirs)
            tc.variables["OPENSSL_FOUND"] = True
        if self.options.get_safe("with_sqlite"):
            tc.variables["SQLITE3_PREFIX"] = self._cmakify_path_list(self.dependencies["sqlite3"].package_folder)
        if self.options.get_safe("with_mysql"):
            tc.variables["MYSQL_LIBRARIES"] = self._cmakify_path_list(self._find_libraries("libmysqlclient"))
            libmysqlclient_cppinfo = self.dependencies["libmysqlclient"].cpp_info.aggregated_components()
            tc.variables["MYSQL_INCLUDE"] = self._cmakify_path_list(libmysqlclient_cppinfo.includedirs)
            tc.variables["MYSQL_DEFINITIONS"] = ";".join(f"-D{d}" for d in libmysqlclient_cppinfo.defines)
            tc.variables["MYSQL_FOUND"] = True
        if self.options.get_safe("with_postgres"):
            tc.variables["POSTGRES_PREFIX"] = self._cmakify_path_list(self.dependencies["libpq"].package_folder)
            tc.variables["POSTGRES_LIBRARIES"] = self._cmakify_path_list(self._find_libraries("libpq"))
            tc.variables["POSTGRES_INCLUDE"] = self._cmakify_path_list(self.dependencies["libpq"].cpp_info.aggregated_components().includedirs)
            tc.variables["POSTGRES_FOUND"] = True
        if self.options.get_safe("with_mssql") and self.settings.os != "Windows":
            tc.variables["ODBC_PREFIX"] = self._cmakify_path_list(self.dependencies["odbc"].package_folder)
            tc.variables["ODBC_LIBRARIES"] = self._cmakify_path_list(self._find_libraries("odbc"))
            tc.variables["ODBC_INCLUDE"] = self._cmakify_path_list(self.dependencies["odbc"].cpp_info.aggregated_components().includedirs)
            tc.variables["ODBC_FOUND"] = True
        if self.options.get_safe("with_unwind"):
            tc.variables["UNWIND_PREFIX"] = self._cmakify_path_list(self.dependencies["libunwind"].package_folder)
        if self.settings.os == "Windows":
            tc.variables["CONNECTOR_FCGI"] = False
            tc.variables["CONNECTOR_ISAPI"] = self.options.connector_isapi
        else:
            tc.variables["CONNECTOR_FCGI"] = self.options.connector_fcgi
            tc.variables["CONNECTOR_ISAPI"] = False

        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        replace_in_file(self, cmakelists, "find_package(OpenSSL)", "#find_package(OpenSSL)")
        replace_in_file(self, cmakelists, "INCLUDE(cmake/WtFindMysql.txt)", "#INCLUDE(cmake/WtFindMysql.txt)")
        replace_in_file(self, cmakelists, "INCLUDE(cmake/WtFindPostgresql.txt)", "#INCLUDE(cmake/WtFindPostgresql.txt)")
        if self.settings.os != "Windows":
            replace_in_file(self, cmakelists, "INCLUDE(cmake/WtFindOdbc.txt)", "#INCLUDE(cmake/WtFindOdbc.txt)")

        # Do not pollute rpath of shared libs of the install tree on macOS please
        replace_in_file(self,
            cmakelists,
            "IF(APPLE)\n  SET(CMAKE_INSTALL_RPATH \"${CMAKE_INSTALL_PREFIX}/lib\")",
            "if(0)",
        )

        replace_in_file(self,
            os.path.join(self.source_folder, "src", "CMakeLists.txt"),
            "TARGET_LINK_LIBRARIES(wt PRIVATE Crypt32.lib)",
            "TARGET_LINK_LIBRARIES(wt PUBLIC crypt32)"
        )

        dbo_cmakelsts = os.path.join(self.source_folder, "src", "Wt", "Dbo", "backend", "CMakeLists.txt")
        replace_in_file(self, dbo_cmakelsts, "FIND_PACKAGE( Sqlite3 REQUIRED)", "FIND_PACKAGE( SQLite3 REQUIRED)")
        replace_in_file(self, dbo_cmakelsts, '${SQLITE3_LIBRARIES}', '${SQLite3_LIBRARIES}')

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        shutil.move(os.path.join(self.package_folder, "share", "Wt"), os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "var"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "wt")

        suffix = "d" if self.settings.build_type == "Debug" else ""

        # wt
        self.cpp_info.components["wtmain"].set_property("cmake_target_name", "Wt::Wt")
        self.cpp_info.components["wtmain"].libs = ["wt{}".format(suffix)]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["wtmain"].system_libs = ["m", "rt"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["wtmain"].system_libs = ["ws2_32", "mswsock", "winmm"]
            if Version(self.version) >= "4.9.0":
                self.cpp_info.components["wtmain"].system_libs.extend(["dwrite", "d2d1", "shlwapi"])
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
