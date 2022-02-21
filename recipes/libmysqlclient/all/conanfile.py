from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
import os


class LibMysqlClientCConan(ConanFile):
    name = "libmysqlclient"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A MySQL client library for C development."
    topics = ("conan", "mysql", "sql", "connector", "database")
    homepage = "https://dev.mysql.com/downloads/mysql/"
    license = "GPL-2.0"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "with_ssl": [True, False], "with_zlib": [True, False]}
    default_options = {"shared": False, "fPIC": True, "with_ssl": True, "with_zlib": True}

    _cmake = None

    @property
    def _with_zstd(self):
        return tools.Version(self.version) > "8.0.17"

    @property
    def _with_lz4(self):
        return tools.Version(self.version) > "8.0.17"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if self.options.with_ssl:
            self.requires("openssl/1.1.1k")

        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self._with_zstd:
            self.requires("zstd/1.5.0")
        if self._with_lz4:
            self.requires("lz4/1.9.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _patch_files(self):
        libs_to_remove = ["icu", "libevent", "re2", "rapidjson", "protobuf", "libedit"]
        if not self._with_lz4:
            libs_to_remove.append("lz4")
        for lib in libs_to_remove:
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                "MYSQL_CHECK_%s()\n" % lib.upper(),
                "",
                strict=False)
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                "INCLUDE(%s)\n" % lib,
                "",
                strict=False)
        tools.rmdir(os.path.join(self._source_subfolder, "extra"))
        for folder in ['client', 'man', 'mysql-test', "libbinlogstandalone"]:
            tools.rmdir(os.path.join(self._source_subfolder, folder))
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                "ADD_SUBDIRECTORY(%s)\n" % folder,
                "",
                strict=False)
        tools.rmdir(os.path.join(self._source_subfolder, "storage", "ndb"))
        for t in ["INCLUDE(cmake/boost.cmake)\n", "MYSQL_CHECK_EDITLINE()\n"]:
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                t,
                "",
                strict=False)
        if self._with_zstd:
            tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "zstd.cmake"),
                "NAMES zstd",
                "NAMES zstd %s" % self.deps_cpp_info["zstd"].libs[0])

        tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "ssl.cmake"),
            "NAMES ssl",
            "NAMES ssl %s" % self.deps_cpp_info["openssl"].components["ssl"].libs[0])

        tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "ssl.cmake"),
            "NAMES crypto",
            "NAMES crypto %s" % self.deps_cpp_info["openssl"].components["crypto"].libs[0])
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        sources_cmake = os.path.join(self._source_subfolder, "CMakeLists.txt")
        sources_cmake_orig = os.path.join(self._source_subfolder, "CMakeListsOriginal.txt")
        tools.rename(sources_cmake, sources_cmake_orig)
        tools.rename("CMakeLists.txt", sources_cmake)
        if self.settings.os == "Macos":
            tools.replace_in_file(os.path.join(self._source_subfolder, "libmysql", "CMakeLists.txt"),
                "COMMAND %s" % ("$<TARGET_FILE:libmysql_api_test>" if tools.Version(self.version) < "8.0.25" else "libmysql_api_test"),
                "COMMAND DYLD_LIBRARY_PATH=%s %s" %(os.path.join(self.build_folder, "library_output_directory"), os.path.join(self.build_folder, "runtime_output_directory", "libmysql_api_test")))
        tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "install_macros.cmake"),
            "  INSTALL_DEBUG_SYMBOLS(",
            "  # INSTALL_DEBUG_SYMBOLS(")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler == "Visual Studio":
            if tools.Version(self.version) > "8.0.17":
                if Version(self.settings.compiler.version) < "16":
                    raise ConanInvalidConfiguration("Visual Studio 16 2019 or newer is required")
            else:
                if Version(self.settings.compiler.version) < "15":
                    raise ConanInvalidConfiguration("Visual Studio 15 2017 or newer is required")
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "5.3":
            raise ConanInvalidConfiguration("GCC 5.3 or newer is required")
        if self.settings.compiler == "clang" and Version(self.settings.compiler.version) < "6":
            raise ConanInvalidConfiguration("clang 6 or newer is required")
        if hasattr(self, "settings_build") and tools.cross_building(self, skip_x64_x86=True):
            raise ConanInvalidConfiguration("Cross compilation not yet supported by the recipe. contributions are welcome.")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["DISABLE_SHARED"] = not self.options.shared
        self._cmake.definitions["STACK_DIRECTION"] = "-1"  # stack grows downwards, on very few platforms stack grows upwards
        self._cmake.definitions["WITHOUT_SERVER"] = True
        self._cmake.definitions["WITH_UNIT_TESTS"] = False
        self._cmake.definitions["ENABLED_PROFILING"] = False
        self._cmake.definitions["WIX_DIR"] = False
        if self._with_lz4:
            self._cmake.definitions["WITH_LZ4"] = "system"

        if self._with_zstd:
            self._cmake.definitions["WITH_ZSTD"] = "system"
            self._cmake.definitions["ZSTD_INCLUDE_DIR"] = self.deps_cpp_info["zstd"].include_paths[0]

        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["WINDOWS_RUNTIME_MD"] = "MD" in str(self.settings.compiler.runtime)

        if self.options.with_ssl:
            self._cmake.definitions["WITH_SSL"] = self.deps_cpp_info["openssl"].rootpath

        if self.options.with_zlib:
            self._cmake.definitions["WITH_ZLIB"] = "system"
        self._cmake.configure(source_dir=self._source_subfolder)
        return self._cmake

    def build(self):
        self._patch_files()
        cmake = self._configure_cmake()
        with tools.run_environment(self):
            cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        with tools.run_environment(self):
            cmake.install()
        os.mkdir(os.path.join(self.package_folder, "licenses"))
        tools.rename(os.path.join(self.package_folder, "LICENSE"), os.path.join(self.package_folder, "licenses", "LICENSE"))
        os.remove(os.path.join(self.package_folder, "README"))
        tools.remove_files_by_mask(self.package_folder, "*.pdb")
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "docs"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        if self.settings.os == "Windows" and self.options.shared:
            self.copy("*.dll", "bin", keep_path=False)
        if self.options.shared:
            tools.remove_files_by_mask(self.package_folder, "*.a")
        else:
            tools.remove_files_by_mask(self.package_folder, "*.dll")
            tools.remove_files_by_mask(self.package_folder, "*.dylib")
            tools.remove_files_by_mask(self.package_folder, "*.so*")

    def package_info(self):
        self.cpp_info.libs = ["libmysql" if self.settings.os == "Windows" and self.options.shared else "mysqlclient"]
        self.cpp_info.names["cmake_find_package"] = "MySQL"
        self.cpp_info.names["cmake_find_package_multi"] = "MySQL"
        self.cpp_info.names["pkg_config"] = "mysqlclient"
        if not self.options.shared:
            stdcpp_library = tools.stdcpp_library(self)
            if stdcpp_library:
                self.cpp_info.system_libs.append(stdcpp_library)
            if self.settings.os == "Linux":
                self.cpp_info.system_libs.append('m')
