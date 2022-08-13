from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import textwrap
import functools

required_conan_version = ">=1.43.0"


class Sqlite3Conan(ConanFile):
    name = "sqlite3"
    description = "Self-contained, serverless, in-process SQL database engine."
    license = "Unlicense"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.sqlite.org"
    topics = ("sqlite", "database", "sql", "serverless")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "threadsafe": [0, 1, 2],
        "enable_column_metadata": [True, False],
        "enable_dbstat_vtab": [True, False],
        "enable_explain_comments": [True, False],
        "enable_fts3": [True, False],
        "enable_fts3_parenthesis": [True, False],
        "enable_fts4": [True, False],
        "enable_fts5": [True, False],
        "enable_json1": [True, False],
        "enable_soundex": [True, False],
        "enable_preupdate_hook": [True, False],
        "enable_rtree": [True, False],
        "use_alloca": [True, False],
        "omit_load_extension": [True, False],
        "omit_deprecated": [True, False],
        "enable_math_functions": [True, False],
        "enable_unlock_notify": [True, False],
        "enable_default_secure_delete": [True, False],
        "disable_gethostuuid": [True, False],
        "max_column": "ANY",
        "max_variable_number": "ANY",
        "max_blob_size": "ANY",
        "build_executable": [True, False],
        "enable_default_vfs": [True, False],
        "enable_dbpage_vtab": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "threadsafe": 1,
        "enable_column_metadata": True,
        "enable_dbstat_vtab": False,
        "enable_explain_comments": False,
        "enable_fts3": False,
        "enable_fts3_parenthesis": False,
        "enable_fts4": False,
        "enable_fts5": False,
        "enable_json1": False,
        "enable_soundex": False,
        "enable_preupdate_hook": False,
        "enable_rtree": True,
        "use_alloca": False,
        "omit_load_extension": False,
        "omit_deprecated": False,
        "enable_math_functions": True,
        "enable_unlock_notify": True,
        "enable_default_secure_delete": False,
        "disable_gethostuuid": False,
        "max_column": None,             # Uses default value from source
        "max_variable_number": None,    # Uses default value from source
        "max_blob_size": None,          # Uses default value from source
        "build_executable": True,
        "enable_default_vfs": True,
        "enable_dbpage_vtab": False,
    }
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _has_enable_math_function_option(self):
        return tools.Version(self.version) >= "3.35.0"

    def export_sources(self):
        self.copy("CMakeLists.txt")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._has_enable_math_function_option:
            del self.options.enable_math_functions

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.options.build_executable:
            if not self.options.enable_default_vfs:
                # Need to provide custom VFS code: https://www.sqlite.org/custombuild.html
                raise ConanInvalidConfiguration("build_executable=True cannot be combined with enable_default_vfs=False")
            if self.options.omit_load_extension:
                raise ConanInvalidConfiguration("build_executable=True requires omit_load_extension=True")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["SQLITE3_VERSION"] = self.version
        cmake.definitions["SQLITE3_BUILD_EXECUTABLE"] = self.options.build_executable
        cmake.definitions["THREADSAFE"] = self.options.threadsafe
        cmake.definitions["ENABLE_COLUMN_METADATA"] = self.options.enable_column_metadata
        cmake.definitions["ENABLE_DBSTAT_VTAB"] = self.options.enable_dbstat_vtab
        cmake.definitions["ENABLE_EXPLAIN_COMMENTS"] = self.options.enable_explain_comments
        cmake.definitions["ENABLE_FTS3"] = self.options.enable_fts3
        cmake.definitions["ENABLE_FTS3_PARENTHESIS"] = self.options.enable_fts3_parenthesis
        cmake.definitions["ENABLE_FTS4"] = self.options.enable_fts4
        cmake.definitions["ENABLE_FTS5"] = self.options.enable_fts5
        cmake.definitions["ENABLE_JSON1"] = self.options.enable_json1
        cmake.definitions["ENABLE_PREUPDATE_HOOK"] = self.options.enable_preupdate_hook
        cmake.definitions["ENABLE_SOUNDEX"] = self.options.enable_soundex
        cmake.definitions["ENABLE_RTREE"] = self.options.enable_rtree
        cmake.definitions["ENABLE_UNLOCK_NOTIFY"] = self.options.enable_unlock_notify
        cmake.definitions["ENABLE_DEFAULT_SECURE_DELETE"] = self.options.enable_default_secure_delete
        cmake.definitions["USE_ALLOCA"] = self.options.use_alloca
        cmake.definitions["OMIT_LOAD_EXTENSION"] = self.options.omit_load_extension
        cmake.definitions["OMIT_DEPRECATED"] = self.options.omit_deprecated
        if self._has_enable_math_function_option:
            cmake.definitions["ENABLE_MATH_FUNCTIONS"] = self.options.enable_math_functions
        cmake.definitions["HAVE_FDATASYNC"] = True
        cmake.definitions["HAVE_GMTIME_R"] = True
        cmake.definitions["HAVE_LOCALTIME_R"] = self.settings.os != "Windows"
        cmake.definitions["HAVE_POSIX_FALLOCATE"] = not (self.settings.os in ["Windows", "Android"] or tools.is_apple_os(self.settings.os))
        cmake.definitions["HAVE_STRERROR_R"] = True
        cmake.definitions["HAVE_USLEEP"] = True
        cmake.definitions["DISABLE_GETHOSTUUID"] = self.options.disable_gethostuuid
        if self.options.max_column:
            cmake.definitions["MAX_COLUMN"] = self.options.max_column
        if self.options.max_variable_number:
            cmake.definitions["MAX_VARIABLE_NUMBER"] = self.options.max_variable_number
        if self.options.max_blob_size:
            cmake.definitions["MAX_BLOB_SIZE"] = self.options.max_blob_size
        cmake.definitions["DISABLE_DEFAULT_VFS"] = not self.options.enable_default_vfs
        cmake.definitions["ENABLE_DBPAGE_VTAB"] = self.options.enable_dbpage_vtab

        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        header = tools.load(os.path.join(self._source_subfolder, "sqlite3.h"))
        license_content = header[3:header.find("***", 1)]
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), license_content)
        cmake = self._configure_cmake()
        cmake.install()

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        #       Indeed CMakeDeps uses 'cmake_file_name' property to qualify CMake variables
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_file_rel_path)
        )

    @staticmethod
    def _create_cmake_module_variables(module_file):
        content = textwrap.dedent("""\
            if(DEFINED SQLite_INCLUDE_DIRS)
                set(SQLite3_INCLUDE_DIRS ${SQLite_INCLUDE_DIRS})
            endif()
            if(DEFINED SQLite_LIBRARIES)
                set(SQLite3_LIBRARIES ${SQLite_LIBRARIES})
            endif()
        """)
        tools.save(module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-variables.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "SQLite3")
        self.cpp_info.set_property("cmake_target_name", "SQLite::SQLite3")
        self.cpp_info.set_property("pkg_config_name", "sqlite3")

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["sqlite"].libs = ["sqlite3"]
        if self.options.omit_load_extension:
            self.cpp_info.components["sqlite"].defines.append("SQLITE_OMIT_LOAD_EXTENSION")
        if self.settings.os in ["Linux", "FreeBSD"]:
            if self.options.threadsafe:
                self.cpp_info.components["sqlite"].system_libs.append("pthread")
            if not self.options.omit_load_extension:
                self.cpp_info.components["sqlite"].system_libs.append("dl")
            if self.options.enable_fts5 or self.options.get_safe("enable_math_functions"):
                self.cpp_info.components["sqlite"].system_libs.append("m")
        elif self.settings.os == "Windows":
            if self.options.shared:
                self.cpp_info.components["sqlite"].defines.append("SQLITE_API=__declspec(dllimport)")

        if self.options.build_executable:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH env var with : {}".format(bin_path))
            self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "SQLite3"
        self.cpp_info.filenames["cmake_find_package_multi"] = "SQLite3"
        self.cpp_info.names["cmake_find_package"] = "SQLite"
        self.cpp_info.names["cmake_find_package_multi"] = "SQLite"
        self.cpp_info.components["sqlite"].names["cmake_find_package"] = "SQLite3"
        self.cpp_info.components["sqlite"].names["cmake_find_package_multi"] = "SQLite3"
        self.cpp_info.components["sqlite"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["sqlite"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["sqlite"].set_property("cmake_target_name", "SQLite::SQLite3")
        self.cpp_info.components["sqlite"].set_property("pkg_config_name", "sqlite3")

        self.cpp_info.components["sqlite"].builddirs = [os.path.join("lib", "cmake")]
