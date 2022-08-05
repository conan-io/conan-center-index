from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, load, save
from conan.tools.scm import Version
from conans import tools as tools_legacy
import os
import textwrap

required_conan_version = ">=1.47.0"


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

    exports_sources = "CMakeLists.txt"

    @property
    def _has_enable_math_function_option(self):
        return Version(self.version) >= "3.35.0"

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
        if self.info.options.build_executable:
            if not self.info.options.enable_default_vfs:
                # Need to provide custom VFS code: https://www.sqlite.org/custombuild.html
                raise ConanInvalidConfiguration("build_executable=True cannot be combined with enable_default_vfs=False")
            if self.info.options.omit_load_extension:
                raise ConanInvalidConfiguration("build_executable=True requires omit_load_extension=True")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SQLITE3_VERSION"] = self.version
        tc.variables["SQLITE3_BUILD_EXECUTABLE"] = self.options.build_executable
        tc.variables["THREADSAFE"] = self.options.threadsafe
        tc.variables["ENABLE_COLUMN_METADATA"] = self.options.enable_column_metadata
        tc.variables["ENABLE_DBSTAT_VTAB"] = self.options.enable_dbstat_vtab
        tc.variables["ENABLE_EXPLAIN_COMMENTS"] = self.options.enable_explain_comments
        tc.variables["ENABLE_FTS3"] = self.options.enable_fts3
        tc.variables["ENABLE_FTS3_PARENTHESIS"] = self.options.enable_fts3_parenthesis
        tc.variables["ENABLE_FTS4"] = self.options.enable_fts4
        tc.variables["ENABLE_FTS5"] = self.options.enable_fts5
        tc.variables["ENABLE_JSON1"] = self.options.enable_json1
        tc.variables["ENABLE_PREUPDATE_HOOK"] = self.options.enable_preupdate_hook
        tc.variables["ENABLE_SOUNDEX"] = self.options.enable_soundex
        tc.variables["ENABLE_RTREE"] = self.options.enable_rtree
        tc.variables["ENABLE_UNLOCK_NOTIFY"] = self.options.enable_unlock_notify
        tc.variables["ENABLE_DEFAULT_SECURE_DELETE"] = self.options.enable_default_secure_delete
        tc.variables["USE_ALLOCA"] = self.options.use_alloca
        tc.variables["OMIT_LOAD_EXTENSION"] = self.options.omit_load_extension
        tc.variables["OMIT_DEPRECATED"] = self.options.omit_deprecated
        if self._has_enable_math_function_option:
            tc.variables["ENABLE_MATH_FUNCTIONS"] = self.options.enable_math_functions
        tc.variables["HAVE_FDATASYNC"] = True
        tc.variables["HAVE_GMTIME_R"] = True
        tc.variables["HAVE_LOCALTIME_R"] = self.settings.os != "Windows"
        tc.variables["HAVE_POSIX_FALLOCATE"] = not (self.settings.os in ["Windows", "Android"] or tools_legacy.is_apple_os(self.settings.os))
        tc.variables["HAVE_STRERROR_R"] = True
        tc.variables["HAVE_USLEEP"] = True
        tc.variables["DISABLE_GETHOSTUUID"] = self.options.disable_gethostuuid
        if self.options.max_column:
            tc.variables["MAX_COLUMN"] = self.options.max_column
        if self.options.max_variable_number:
            tc.variables["MAX_VARIABLE_NUMBER"] = self.options.max_variable_number
        if self.options.max_blob_size:
            tc.variables["MAX_BLOB_SIZE"] = self.options.max_blob_size
        tc.variables["DISABLE_DEFAULT_VFS"] = not self.options.enable_default_vfs
        tc.variables["ENABLE_DBPAGE_VTAB"] = self.options.enable_dbpage_vtab
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def _extract_license(self):
        header = load(self, os.path.join(self.source_folder, "sqlite3.h"))
        license_content = header[3:header.find("***", 1)]
        return license_content

    def package(self):
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._extract_license())
        cmake = CMake(self)
        cmake.install()

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        #       Indeed CMakeDeps uses 'cmake_file_name' property to qualify CMake variables
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_file_rel_path)
        )

    def _create_cmake_module_variables(self, module_file):
        content = textwrap.dedent("""\
            if(DEFINED SQLite_INCLUDE_DIRS)
                set(SQLite3_INCLUDE_DIRS ${SQLite_INCLUDE_DIRS})
            endif()
            if(DEFINED SQLite_LIBRARIES)
                set(SQLite3_LIBRARIES ${SQLite_LIBRARIES})
            endif()
        """)
        save(self, module_file, content)

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
