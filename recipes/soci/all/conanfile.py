import os
from conans import ConanFile, CMake, tools
from conans.tools import Version
from conans.errors import ConanInvalidConfiguration, ConanException

class SociConan(ConanFile):
    name = "soci"
    homepage = "https://github.com/SOCI/soci"
    url = "https://github.com/conan-io/conan-center-index"
    description = "The C++ Database Access Library "
    topics = ("cpp", "database-library", "oracle", "postgresql", "mysql", "odbc", "db2", "firebird", "sqlite3", "boost" )
    license = "BSL-1.0"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    exports_sources = ["CMakeLists.txt"]
    _cmake = None

    options = {
        "fPIC":             [True, False],
        "shared":           [True, False],
        "empty":            [True, False],
        "with_sqlite3":     [True, False],
        "with_db2":         [True, False],
        "with_odbc":        [True, False],
        "with_oracle":      [True, False],
        "with_firebird":    [True, False],
        "with_mysql":       [True, False],
        "with_postgresql":  [True, False],
        "with_boost":       [True, False]
    }

    default_options = {
        "fPIC":             True,
        "shared":           False,
        "empty":            False,
        "with_sqlite3":     False,
        "with_db2":         False,
        "with_odbc":        False,
        "with_oracle":      False,
        "with_firebird":    False,
        "with_mysql":       False,
        "with_postgresql":  False,
        "with_boost":       False
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minimum_cpp_standard(self):
        return 11

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "14",
            "gcc": "4.8",
            "clang": "3.8",
            "apple-clang": "8.0"
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        compiler = str(self.settings.compiler)
        compiler_version = Version(self.settings.compiler.version.value)
        tools.check_min_cppstd(self, self._minimum_cpp_standard)

        if compiler not in self._minimum_compilers_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(self.name, self.settings.compiler))
        elif compiler_version < self._minimum_compilers_version[compiler]:
            raise ConanInvalidConfiguration("{} requires a {} version >= {}".format(self.name, compiler, compiler_version))

    def requirements(self):
        prefix  = "Dependencies for "
        message = " not configured in this conan package."

        if self.options.with_sqlite3:
            self.requires("sqlite3/3.33.0")
        if self.options.with_db2:
            # self.requires("db2/0.0.0") # TODO add support for db2
            raise ConanInvalidConfiguration(prefix + "DB2" + message)
        if self.options.with_odbc:
            self.requires("odbc/2.3.7")
        if self.options.with_oracle:
            # self.requires("oracle_db/0.0.0") # TODO add support for oracle
            raise ConanInvalidConfiguration(prefix + "ORACLE" + message)
        if self.options.with_firebird:
            # self.requires("firebird/0.0.0") # TODO add support for firebird
            raise ConanInvalidConfiguration(prefix + "firebird" + message)
        if self.options.with_mysql:
            self.requires("libmysqlclient/8.0.17")
        if self.options.with_postgresql:
            self.requires("libpq/11.5")
        if self.options.with_boost:
            self.requires("boost/1.73.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)

        self._cmake.definitions["SOCI_SHARED"]  = self.options.shared
        self._cmake.definitions["SOCI_TESTS"]   = False
        self._cmake.definitions["SOCI_CXX11"]   = True

        if self.options.shared:
            self._cmake.definitions["SOCI_STATIC"] = False

        self._cmake.definitions["SOCI_EMPTY"]       = self.options.empty
        self._cmake.definitions["WITH_SQLITE3"]     = self.options.with_sqlite3
        self._cmake.definitions["WITH_DB2"]         = self.options.with_db2
        self._cmake.definitions["WITH_ODBC"]        = self.options.with_odbc
        self._cmake.definitions["WITH_ORACLE"]      = self.options.with_oracle
        self._cmake.definitions["WITH_FIREBIRD"]    = self.options.with_firebird
        self._cmake.definitions["WITH_MYSQL"]       = self.options.with_mysql
        self._cmake.definitions["WITH_POSTGRESQL"]  = self.options.with_postgresql
        self._cmake.definitions["WITH_BOOST"]       = self.options.with_boost

        self._cmake.configure()

        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        include_folder  = os.path.join(self._source_subfolder, "include")

        self.copy("*.h",    dst="include", src=include_folder)
        self.copy("*soci*.lib", dst="lib", src="lib", keep_path=False, symlinks=True)
        self.copy("*soci*.so*", dst="lib", src="lib", keep_path=False, symlinks=True)
        self.copy("*.a",        dst="lib", src="lib", keep_path=False, symlinks=True)
        self.copy("*.dylib",    dst="lib", src="lib", keep_path=False, symlinks=True)
        self.copy("*.dll",      dst="bin", src="bin", keep_path=False, symlinks=True)
        self.copy("LICENSE_1_0.txt", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.includedirs   = ['include']
        self.cpp_info.libdirs       = ['lib', 'lib64']
        self.cpp_info.builddirs     = ['cmake']

        self.cpp_info.libs = [""]

        if self.options.shared:
            self.cpp_info.libs.append("soci_core")
            if self.options.empty:
                self.cpp_info.libs.append("soci_empty")
            if self.options.with_sqlite3:
                self.cpp_info.libs.append("soci_sqlite3")
            if self.options.with_oracle:
                self.cpp_info.libs.append("soci_oracle")
            if self.options.with_mysql:
                self.cpp_info.libs.append("soci_mysql")
            if self.options.with_postgresql:
                self.cpp_info.libs.append("soci_postgresql")

        if self._cmake:
            self._cmake.install()
