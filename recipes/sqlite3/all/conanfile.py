from conans import ConanFile, CMake, tools
import os
import textwrap

required_conan_version = ">=1.33.0"


class ConanSqlite3(ConanFile):
    name = "sqlite3"
    description = "Self-contained, serverless, in-process SQL database engine."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.sqlite.org"
    topics = ("conan", "sqlite", "database", "sql", "serverless")
    license = "Unlicense"
    generators = "cmake"
    settings = "os", "compiler", "arch", "build_type"
    exports_sources = ["CMakeLists.txt"]
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
        "enable_math_functions": [True, False],
        "enable_unlock_notify": [True, False],
        "enable_default_secure_delete": [True, False],
        "disable_gethostuuid": [True, False],
        "max_blob_size": "ANY",
        "build_executable": [True, False],
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
        "enable_math_functions": True,
        "enable_unlock_notify": True,
        "enable_default_secure_delete": False,
        "disable_gethostuuid": False,
        "max_blob_size": 1000000000,
        "build_executable": True,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _has_enable_math_function_option(self):
        return tools.Version(self.version) >= "3.35.0"

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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        url = self.conan_data["sources"][self.version]["url"]
        archive_name = os.path.basename(url)
        archive_name = os.path.splitext(archive_name)[0]
        os.rename(archive_name, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["SQLITE3_VERSION"] = self.version
        self._cmake.definitions["SQLITE3_BUILD_EXECUTABLE"] = self.options.build_executable
        self._cmake.definitions["THREADSAFE"] = self.options.threadsafe
        self._cmake.definitions["ENABLE_COLUMN_METADATA"] = self.options.enable_column_metadata
        self._cmake.definitions["ENABLE_DBSTAT_VTAB"] = self.options.enable_dbstat_vtab
        self._cmake.definitions["ENABLE_EXPLAIN_COMMENTS"] = self.options.enable_explain_comments
        self._cmake.definitions["ENABLE_FTS3"] = self.options.enable_fts3
        self._cmake.definitions["ENABLE_FTS3_PARENTHESIS"] = self.options.enable_fts3_parenthesis
        self._cmake.definitions["ENABLE_FTS4"] = self.options.enable_fts4
        self._cmake.definitions["ENABLE_FTS5"] = self.options.enable_fts5
        self._cmake.definitions["ENABLE_JSON1"] = self.options.enable_json1
        self._cmake.definitions["ENABLE_PREUPDATE_HOOK"] = self.options.enable_preupdate_hook
        self._cmake.definitions["ENABLE_SOUNDEX"] = self.options.enable_soundex
        self._cmake.definitions["ENABLE_RTREE"] = self.options.enable_rtree
        self._cmake.definitions["ENABLE_UNLOCK_NOTIFY"] = self.options.enable_unlock_notify
        self._cmake.definitions["ENABLE_DEFAULT_SECURE_DELETE"] = self.options.enable_default_secure_delete
        self._cmake.definitions["USE_ALLOCA"] = self.options.use_alloca
        self._cmake.definitions["OMIT_LOAD_EXTENSION"] = self.options.omit_load_extension
        if self._has_enable_math_function_option:
            self._cmake.definitions["ENABLE_MATH_FUNCTIONS"] = self.options.enable_math_functions
        self._cmake.definitions["HAVE_FDATASYNC"] = True
        self._cmake.definitions["HAVE_GMTIME_R"] = True
        self._cmake.definitions["HAVE_LOCALTIME_R"] = self.settings.os != "Windows"
        self._cmake.definitions["HAVE_POSIX_FALLOCATE"] = not (self.settings.os in ["Windows", "Android"] or tools.is_apple_os(self.settings.os))
        self._cmake.definitions["HAVE_STRERROR_R"] = True
        self._cmake.definitions["HAVE_USLEEP"] = True
        self._cmake.definitions["DISABLE_GETHOSTUUID"] = self.options.disable_gethostuuid
        self._cmake.definitions["MAX_BLOB_SIZE"] = self.options.max_blob_size
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        header = tools.load(os.path.join(self._source_subfolder, "sqlite3.h"))
        license_content = header[3:header.find("***", 1)]
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), license_content)
        cmake = self._configure_cmake()
        cmake.install()
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
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-variables.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "SQLite3"
        self.cpp_info.filenames["cmake_find_package_multi"] = "SQLite3"
        self.cpp_info.names["cmake_find_package"] = "SQLite"
        self.cpp_info.names["cmake_find_package_multi"] = "SQLite"
        self.cpp_info.components["sqlite"].names["cmake_find_package"] = "SQLite3"
        self.cpp_info.components["sqlite"].names["cmake_find_package_multi"] = "SQLite3"
        self.cpp_info.components["sqlite"].builddirs.append(self._module_subfolder)
        self.cpp_info.components["sqlite"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["sqlite"].libs = tools.collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            if self.options.threadsafe:
                self.cpp_info.components["sqlite"].system_libs.append("pthread")
            if not self.options.omit_load_extension:
                self.cpp_info.components["sqlite"].system_libs.append("dl")
            if self.options.enable_fts5 or self.options.get_safe("enable_math_functions"):
                self.cpp_info.components["sqlite"].system_libs.append("m")

        if self.options.build_executable:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH env var with : {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
