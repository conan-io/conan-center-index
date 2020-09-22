from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil


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
        self.options["boost"].without_program_options = False
        self.options["boost"].without_filesystem = False
        self.options["boost"].without_thread = False

    def requirements(self):
        self.requires("boost/1.74.0")
        if self.options.connector_http:
            self.requires("zlib/1.2.11")
        if self.options.with_ssl:
            self.requires("openssl/1.1.1g")
        if self.options.get_safe("with_sqlite"):
            self.requires("sqlite3/3.32.3")
        if self.options.get_safe("with_mysql"):
            self.requires("libmysqlclient/8.0.17")
        if self.options.get_safe("with_postgres"):
            self.requires("libpq/12.2")
        if self.options.get_safe("with_unwind"):
            self.requires("libunwind/1.3.1")

    def _validate_dependency_graph(self):
        if self.options["boost"].without_program_options or self.options["boost"].without_filesystem or self.options["boost"].without_thread:
            raise ConanInvalidConfiguration("wt depends on these boost components: program_options, filesystem, thread")

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
        self.cpp_info.libs = []
        if self.options.with_test:
            self.cpp_info.libs.append("wttest")
        if self.options.get_safe("with_postgres"):
            self.cpp_info.libs.append("wtdbopostgres")
        if self.options.get_safe("with_sqlite"):
            self.cpp_info.libs.append("wtdbosqlite3")
        if self.options.get_safe("with_mysql"):
            self.cpp_info.libs.append("wtdbomysql")
        if self.options.with_mssql:
            self.cpp_info.libs.append("wtdbomssqlserver")
        if self.options.with_dbo:
            self.cpp_info.libs.append("wtdbo")
        if self.options.connector_http:
            self.cpp_info.libs.append("wthttp")
        if self.settings.os == "Windows":
            if self.options.connector_isapi:
                self.cpp_info.libs.append("wtisapi")
        else:
            if self.options.connector_fcgi:
                self.cpp_info.libs.append("wtfcgi")
        self.cpp_info.libs.append("wt")
        if self.settings.build_type == "Debug":
            self.cpp_info.libs = ["%sd" % lib for lib in self.cpp_info.libs]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("dl")
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "mswsock", "wsock32"])
