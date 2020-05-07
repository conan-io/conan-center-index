import os
from conans import ConanFile, CMake, tools


class ConanSqlite3(ConanFile):
    name = "sqlite3"
    description = "Self-contained, serverless, in-process SQL database engine."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.sqlite.org"
    topics = ("conan", "sqlite", "database", "sql", "serverless")
    license = "Public Domain"
    generators = "cmake"
    settings = "os", "compiler", "arch", "build_type"
    exports_sources = ["CMakeLists.txt"]
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "threadsafe": [0, 1, 2],
               "enable_column_metadata": [True, False],
               "enable_explain_comments": [True, False],
               "enable_fts3": [True, False],
               "enable_fts4": [True, False],
               "enable_fts5": [True, False],
               "enable_json1": [True, False],
               "enable_rtree": [True, False],
               "omit_load_extension": [True, False],
               "enable_unlock_notify": [True, False],
               "disable_gethostuuid": [True, False],
               "build_executable": [True, False],
               }
    default_options = {"shared": False,
                       "fPIC": True,
                       "threadsafe": 1,
                       "enable_column_metadata": True,
                       "enable_explain_comments": False,
                       "enable_fts3": False,
                       "enable_fts4": False,
                       "enable_fts5": False,
                       "enable_json1": False,
                       "enable_rtree": True,
                       "omit_load_extension": False,
                       "enable_unlock_notify": True,
                       "disable_gethostuuid": False,
                       "build_executable": True,
                       }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
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
        self._cmake.definitions["SQLITE3_BUILD_EXECUTABLE"] = self.options.build_executable
        self._cmake.definitions["THREADSAFE"] = self.options.threadsafe
        self._cmake.definitions["ENABLE_COLUMN_METADATA"] = self.options.enable_column_metadata
        self._cmake.definitions["ENABLE_EXPLAIN_COMMENTS"] = self.options.enable_explain_comments
        self._cmake.definitions["ENABLE_FTS3"] = self.options.enable_fts3
        self._cmake.definitions["ENABLE_FTS4"] = self.options.enable_fts4
        self._cmake.definitions["ENABLE_FTS5"] = self.options.enable_fts5
        self._cmake.definitions["ENABLE_JSON1"] = self.options.enable_json1
        self._cmake.definitions["ENABLE_RTREE"] = self.options.enable_rtree
        self._cmake.definitions["OMIT_LOAD_EXTENSION"] = self.options.omit_load_extension
        self._cmake.definitions["SQLITE_ENABLE_UNLOCK_NOTIFY"] = self.options.enable_unlock_notify
        self._cmake.definitions["HAVE_FDATASYNC"] = True
        self._cmake.definitions["HAVE_GMTIME_R"] = True
        self._cmake.definitions["HAVE_LOCALTIME_R"] = self.settings.os != "Windows"
        self._cmake.definitions["HAVE_POSIX_FALLOCATE"] = not (self.settings.os in ["Windows", "Android"] or tools.is_apple_os(self.settings.os))
        self._cmake.definitions["HAVE_STRERROR_R"] = True
        self._cmake.definitions["HAVE_USLEEP"] = True
        self._cmake.definitions["DISABLE_GETHOSTUUID"] = self.options.disable_gethostuuid
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

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            if self.options.threadsafe:
                self.cpp_info.system_libs.append("pthread")
            if not self.options.omit_load_extension:
                self.cpp_info.system_libs.append("dl")
        if self.options.build_executable:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH env var with : {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
