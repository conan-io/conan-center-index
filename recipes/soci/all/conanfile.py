import os
from conans import ConanFile, CMake, tools
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
    _cmake = None

    options = {
        "fPIC":             [True, False],
        "empty":            [True, False],
        "shared":           [True, False],
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
        "empty":            True,
        "shared":           False,
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
    def _build_subfolder(self):
        return "build_subfolder"

    def _validate_compiler_settings(self):
        tools.check_min_cppstd(self, "11")
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "5.0":
            raise ConanInvalidConfiguration("gcc minimum required version is 5.0")
        elif self.settings.compiler == "clang" and tools.Version(self.settings.compiler.version) < "3.8":
            raise ConanInvalidConfiguration("clang minimum required version is 3.8")
        elif self.settings.compiler == "apple-clang" and tools.Version(self.settings.compiler.version) < "10.0":
            raise ConanInvalidConfiguration("apple-clang minimum required version is 10.0")
        elif self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version) < "19":
            raise ConanInvalidConfiguration("Visual Studio minimum required version is 19")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        self._validate_compiler_settings()

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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)

        self._cmake.definitions["SOCI_EMPTY"]       = self.options.empty
        self._cmake.definitions["SOCI_SHARED"]      = self.options.shared
        self._cmake.definitions["WITH_SQLITE3"]     = self.options.with_sqlite3
        self._cmake.definitions["WITH_DB2"]         = self.options.with_db2
        self._cmake.definitions["WITH_ODBC"]        = self.options.with_odbc
        self._cmake.definitions["WITH_ORACLE"]      = self.options.with_oracle
        self._cmake.definitions["WITH_FIREBIRD"]    = self.options.with_firebird
        self._cmake.definitions["WITH_MYSQL"]       = self.options.with_mysql
        self._cmake.definitions["WITH_POSTGRESQL"]  = self.options.with_postgresql
        self._cmake.definitions["WITH_BOOST"]       = self.options.with_boost
        self._cmake.definitions["SOCI_CXX11"]       = True

        self._cmake.configure(
            source_folder=self._source_subfolder,
            build_folder=self._build_subfolder)

        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        include_folder  = os.path.join(self._source_subfolder, "include")
        lib_folder      = os.path.join(self._build_subfolder, "lib")
        bin_folder      = os.path.join(self._build_subfolder, "bin")

        self.copy("*.h",    dst="include", src=include_folder)
        self.copy("*soci*.lib", dst="lib", src=lib_folder, keep_path=False, symlinks=True)
        self.copy("*soci*.so*", dst="lib", src=lib_folder, keep_path=False, symlinks=True)
        self.copy("*.a",        dst="lib", src=lib_folder, keep_path=False, symlinks=True)
        self.copy("*.dylib",    dst="lib", src=lib_folder, keep_path=False, symlinks=True)
        self.copy("*.dll",      dst="bin", src=bin_folder, keep_path=False, symlinks=True)
        self.copy("LICENSE_1_0.txt", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.includedirs   = ['include']
        self.cpp_info.libdirs       = ['lib', 'lib64']
        self.cpp_info.builddirs     = ['cmake']

        self.cpp_info.libs = [""]
        if self.options.empty:
            self.cpp_info.libs.append("soci_empty")

        if self.options.shared:
            self.cpp_info.libs.append("soci_core")
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
