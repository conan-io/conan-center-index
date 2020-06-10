from conans import ConanFile, CMake, tools
from conans.client.build.cppstd_flags import cppstd_default
from conans.errors import ConanInvalidConfiguration, ConanException
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
        "odbc": False,
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

    def configure(self):
        compiler = str(self.settings.compiler)
        if compiler == "apple-clang" and tools.Version(self.settings.compiler.version) <= "9.1":
            raise ConanInvalidConfiguration( "{} requires at least {} 9.1".format(self.name, compiler))
        if compiler == "clang" and tools.Version(self.settings.compiler.version) <= "5.0":
            raise ConanInvalidConfiguration( "{} requires at least {} 5.0".format(self.name, compiler))

    def requirements(self):
        if self.options.with_backend_sqlite3:
            self.requires("sqlite3/3.31.1")

        if self.options.with_backend_mysql:
            self.requires("libmysqlclient/8.0.17")

        if self.options.with_backend_odbc:
            self.requires("odbc/2.3.7")

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

    def _get_cppstd(self):
        cppstd = self.settings.get_safe("compiler.cppstd")
        if cppstd is None:
            cppstd = cppstd_default(self.settings)

        compiler = self.settings.get_safe("compiler")
        compiler_version = self.settings.get_safe("compiler.version")
        if not compiler or not compiler_version:
            raise ConanException("Could not obtain cppstd because there is no declared "
                                 "compiler in the 'settings' field of the recipe.")

        if cppstd is None:
            raise ConanInvalidConfiguration("Could not detect the current default cppstd for "
                                            "the compiler {}-{}.".format(compiler,
                                                                         compiler_version))

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

        self._cmake.definitions["SOCI_CXX11"] = True

        cppstd = self._get_cppstd()
        if cppstd == "98" or cppstd == "gnu98":
            self._cmake.definitions["SOCI_CXX11"] = False



        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

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
            prefix = ""
            if not self.options.shared:
                prefix = "lib"

            abi_version = tools.Version(self.version)
            name = "{prefix}{name}_{major}_{minor}".format(
                prefix = prefix,
                name = name,
                major = abi_version.major,
                minor = abi_version.minor
            )
        return name

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Soci"
        self.cpp_info.names["cmake_find_package_multi"] = "Soci"

        self.cpp_info.components["core"].libs = [self._construct_library_name("soci_core")]

        cppstd = self._get_cppstd()
        self.cpp_info.components["core"].defines = ["CMAKE_CXX_STANDARD={}".format("98" if cppstd == "98" or cppstd == "gnu98" else "11")]

        if self.options.with_boost:
            self.cpp_info.components["core"].defines.append("SOCI_USE_BOOST")
            self.cpp_info.components["core"].requires.append("boost::date_time")
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
