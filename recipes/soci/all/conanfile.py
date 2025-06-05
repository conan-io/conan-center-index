from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=2.1"


class SociConan(ConanFile):
    name = "soci"
    homepage = "https://github.com/SOCI/soci"
    url = "https://github.com/conan-io/conan-center-index"
    description = "The C++ Database Access Library "
    topics = ("mysql", "odbc", "postgresql", "sqlite3")
    license = "BSL-1.0"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared":           [True, False],
        "fPIC":             [True, False],
        "empty":            [True, False],
        "with_sqlite3":     [True, False],
        "with_odbc":        [True, False],
        "with_mysql":       [True, False],
        "with_postgresql":  [True, False],
        "with_boost":       [True, False],
    }
    default_options = {
        "shared":           False,
        "fPIC":             True,
        "empty":            False,
        "with_sqlite3":     False,
        "with_odbc":        False,
        "with_mysql":       False,
        "with_postgresql":  False,
        "with_boost":       False,
    }

    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # New versions will not need transitive_headers=True
        if self.options.with_sqlite3:
            self.requires("sqlite3/[>=3.44 <4]", transitive_headers=True)
        if self.options.with_odbc and self.settings.os != "Windows":
            self.requires("odbc/2.3.11", transitive_headers=True)
        if self.options.with_mysql:
            self.requires("libmysqlclient/8.1.0", transitive_headers=True)
        if self.options.with_postgresql:
            self.requires("libpq/15.4", transitive_headers=True)
        if self.options.with_boost:
            self.requires("boost/1.83.0", transitive_headers=True)

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)

        # MacOS @rpath
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.cache_variables["SOCI_SHARED"] = self.options.shared
        tc.cache_variables["SOCI_STATIC"] = not self.options.shared
        tc.cache_variables["SOCI_TESTS"] = False
        tc.cache_variables["SOCI_CXX11"] = True
        tc.cache_variables["SOCI_EMPTY"] = self.options.empty
        tc.cache_variables["WITH_SQLITE3"] = self.options.with_sqlite3
        tc.cache_variables["WITH_DB2"] = False
        tc.cache_variables["WITH_ODBC"] = self.options.with_odbc
        tc.cache_variables["WITH_ORACLE"] = False
        tc.cache_variables["WITH_FIREBIRD"] = False
        tc.cache_variables["WITH_MYSQL"] = self.options.with_mysql
        tc.cache_variables["WITH_POSTGRESQL"] = self.options.with_postgresql
        tc.cache_variables["WITH_BOOST"] = self.options.with_boost
        if Version(self.version) < "4.1.0": # pylint: disable=conan-condition-evals-to-constant
            tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5" # CMake 4 support
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("mysql", "cmake_file_name", "MYSQL")
        deps.set_property("libpq", "cmake_file_name", "POSTGRESQL")
        deps.set_property("sqlite3", "cmake_file_name", "SQLite3")
        deps.set_property("sqlite3", "cmake_additional_variables_prefixes", ["SQLITE3"])
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE_1_0.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SOCI")

        target_suffix = "" if self.options.shared else "_static"
        lib_prefix = "lib" if is_msvc(self) and not self.options.shared else ""
        version = Version(self.version)
        lib_suffix = "_{}_{}".format(version.major, version.minor) if self.settings.os == "Windows" else ""

        # soci_core
        self.cpp_info.components["soci_core"].set_property("cmake_target_name", "SOCI::soci_core{}".format(target_suffix))
        self.cpp_info.components["soci_core"].libs = ["{}soci_core{}".format(lib_prefix, lib_suffix)]
        if self.options.with_boost:
            self.cpp_info.components["soci_core"].requires.append("boost::headers")

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
