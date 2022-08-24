from conan.tools.files import rename
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class SociConan(ConanFile):
    name = "soci"
    homepage = "https://github.com/SOCI/soci"
    url = "https://github.com/conan-io/conan-center-index"
    description = "The C++ Database Access Library "
    topics = ("mysql", "odbc", "postgresql", "sqlite3")
    license = "BSL-1.0"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared":           [True, False],
        "fPIC":             [True, False],
        "empty":            [True, False],
        "with_sqlite3":     [True, False],
        "with_db2":         [True, False],
        "with_odbc":        [True, False],
        "with_oracle":      [True, False],
        "with_firebird":    [True, False],
        "with_mysql":       [True, False],
        "with_postgresql":  [True, False],
        "with_boost":       [True, False],
    }
    default_options = {
        "shared":           False,
        "fPIC":             True,
        "empty":            False,
        "with_sqlite3":     False,
        "with_db2":         False,
        "with_odbc":        False,
        "with_oracle":      False,
        "with_firebird":    False,
        "with_mysql":       False,
        "with_postgresql":  False,
        "with_boost":       False,
    }

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.with_sqlite3:
            self.requires("sqlite3/3.38.0")
        if self.options.with_odbc and self.settings.os != "Windows":
            self.requires("odbc/2.3.9")
        if self.options.with_mysql:
            self.requires("libmysqlclient/8.0.25")
        if self.options.with_postgresql:
            self.requires("libpq/13.4")
        if self.options.with_boost:
            self.requires("boost/1.78.0")

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "14",
            "gcc": "4.8",
            "clang": "3.8",
            "apple-clang": "8.0"
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, 11)

        compiler = str(self.settings.compiler)
        compiler_version = tools.scm.Version(self, self.settings.compiler.version.value)
        if compiler not in self._minimum_compilers_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(self.name, self.settings.compiler))
        elif compiler_version < self._minimum_compilers_version[compiler]:
            raise ConanInvalidConfiguration("{} requires a {} version >= {}".format(self.name, compiler, compiler_version))

        prefix  = "Dependencies for"
        message = "not configured in this conan package."
        if self.options.with_db2:
            # self.requires("db2/0.0.0") # TODO add support for db2
            raise ConanInvalidConfiguration("{} DB2 {} ".format(prefix, message))
        if self.options.with_oracle:
            # self.requires("oracle_db/0.0.0") # TODO add support for oracle
            raise ConanInvalidConfiguration("{} ORACLE {} ".format(prefix, message))
        if self.options.with_firebird:
            # self.requires("firebird/0.0.0") # TODO add support for firebird
            raise ConanInvalidConfiguration("{} firebird {} ".format(prefix, message))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        tools.files.replace_in_file(self, cmakelists,
                              "set(CMAKE_MODULE_PATH ${SOCI_SOURCE_DIR}/cmake ${CMAKE_MODULE_PATH})",
                              "list(APPEND CMAKE_MODULE_PATH ${SOCI_SOURCE_DIR}/cmake)")
        tools.files.replace_in_file(self, cmakelists,
                              "set(CMAKE_MODULE_PATH ${SOCI_SOURCE_DIR}/cmake/modules ${CMAKE_MODULE_PATH})",
                              "list(APPEND CMAKE_MODULE_PATH ${SOCI_SOURCE_DIR}/cmake/modules)")

        # Remove hardcoded install_name_dir, it prevents relocatable shared lib on macOS
        soci_backend_cmake = os.path.join(self._source_subfolder, "cmake", "SociBackend.cmake")
        soci_core_cmake = os.path.join(self._source_subfolder, "src", "core", "CMakeLists.txt")
        tools.files.replace_in_file(self, soci_backend_cmake, "INSTALL_NAME_DIR ${CMAKE_INSTALL_PREFIX}/lib", "")
        tools.files.replace_in_file(self, soci_core_cmake, "INSTALL_NAME_DIR ${CMAKE_INSTALL_PREFIX}/lib", "")

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

        # Relocatable shared lib on macOS
        self._cmake.definitions["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"

        self._cmake.configure()

        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE_1_0.txt", dst="licenses", src=self._source_subfolder)

        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "cmake"))

        if os.path.isdir(os.path.join(self.package_folder, "lib64")):
            if os.path.isdir(os.path.join(self.package_folder, "lib")):
                self.copy("*", dst="lib", src="lib64", keep_path=False, symlinks=True)
                tools.files.rmdir(self, os.path.join(self.package_folder, "lib64"))
            else:
                rename(self, os.path.join(self.package_folder, "lib64"), os.path.join(self.package_folder, "lib"))

        os.remove(os.path.join(self.package_folder, "include", "soci", "soci-config.h.in"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SOCI")

        target_suffix = "" if self.options.shared else "_static"
        lib_prefix = "lib" if self._is_msvc and not self.options.shared else ""
        version = tools.scm.Version(self, self.version)
        lib_suffix = "_{}_{}".format(version.major, version.minor) if self.settings.os == "Windows" else ""

        # soci_core
        self.cpp_info.components["soci_core"].set_property("cmake_target_name", "SOCI::soci_core{}".format(target_suffix))
        self.cpp_info.components["soci_core"].libs = ["{}soci_core{}".format(lib_prefix, lib_suffix)]
        if self.options.with_boost:
            self.cpp_info.components["soci_core"].requires.append("boost::boost")

        # soci_empty
        if self.options.empty:
            self.cpp_info.components["soci_empty"].set_property("cmake_target_name", "SOCI::soci_empty{}".format(target_suffix))
            self.cpp_info.components["soci_empty"].libs = ["{}soci_empty{}".format(lib_prefix, lib_suffix)]
            self.cpp_info.components["soci_empty"].requires = ["soci_core"]

        # soci_sqlite3
        if self.options.with_sqlite3:
            self.cpp_info.components["soci_sqlite3"].set_property("cmake_target_name", "SOCI::soci_sqlite3{}".format(target_suffix))
            self.cpp_info.components["soci_sqlite3"].libs = ["{}soci_sqlite3{}".format(lib_prefix, lib_suffix)]
            self.cpp_info.components["soci_sqlite3"].requires = ["soci_core", "sqlite3::sqlite3"]

        # soci_odbc
        if self.options.with_odbc:
            self.cpp_info.components["soci_odbc"].set_property("cmake_target_name", "SOCI::soci_odbc{}".format(target_suffix))
            self.cpp_info.components["soci_odbc"].libs = ["{}soci_odbc{}".format(lib_prefix, lib_suffix)]
            self.cpp_info.components["soci_odbc"].requires = ["soci_core"]
            if self.settings.os == "Windows":
                self.cpp_info.components["soci_odbc"].system_libs.append("odbc32")
            else:
                self.cpp_info.components["soci_odbc"].requires.append("odbc::odbc")

        # soci_mysql
        if self.options.with_mysql:
            self.cpp_info.components["soci_mysql"].set_property("cmake_target_name", "SOCI::soci_mysql{}".format(target_suffix))
            self.cpp_info.components["soci_mysql"].libs = ["{}soci_mysql{}".format(lib_prefix, lib_suffix)]
            self.cpp_info.components["soci_mysql"].requires = ["soci_core", "libmysqlclient::libmysqlclient"]

        # soci_postgresql
        if self.options.with_postgresql:
            self.cpp_info.components["soci_postgresql"].set_property("cmake_target_name", "SOCI::soci_postgresql{}".format(target_suffix))
            self.cpp_info.components["soci_postgresql"].libs = ["{}soci_postgresql{}".format(lib_prefix, lib_suffix)]
            self.cpp_info.components["soci_postgresql"].requires = ["soci_core", "libpq::libpq"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "SOCI"
        self.cpp_info.names["cmake_find_package_multi"] = "SOCI"
        self.cpp_info.components["soci_core"].names["cmake_find_package"] = "soci_core{}".format(target_suffix)
        self.cpp_info.components["soci_core"].names["cmake_find_package_multi"] = "soci_core{}".format(target_suffix)
        if self.options.empty:
            self.cpp_info.components["soci_empty"].names["cmake_find_package"] = "soci_empty{}".format(target_suffix)
            self.cpp_info.components["soci_empty"].names["cmake_find_package_multi"] = "soci_empty{}".format(target_suffix)
        if self.options.with_sqlite3:
            self.cpp_info.components["soci_sqlite3"].names["cmake_find_package"] = "soci_sqlite3{}".format(target_suffix)
            self.cpp_info.components["soci_sqlite3"].names["cmake_find_package_multi"] = "soci_sqlite3{}".format(target_suffix)
        if self.options.with_odbc:
            self.cpp_info.components["soci_odbc"].names["cmake_find_package"] = "soci_odbc{}".format(target_suffix)
            self.cpp_info.components["soci_odbc"].names["cmake_find_package_multi"] = "soci_odbc{}".format(target_suffix)
        if self.options.with_mysql:
            self.cpp_info.components["soci_mysql"].names["cmake_find_package"] = "soci_mysql{}".format(target_suffix)
            self.cpp_info.components["soci_mysql"].names["cmake_find_package_multi"] = "soci_mysql{}".format(target_suffix)
        if self.options.with_postgresql:
            self.cpp_info.components["soci_postgresql"].names["cmake_find_package"] = "soci_postgresql{}".format(target_suffix)
            self.cpp_info.components["soci_postgresql"].names["cmake_find_package_multi"] = "soci_postgresql{}".format(target_suffix)
