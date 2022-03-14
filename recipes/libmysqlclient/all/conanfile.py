from conan.tools.microsoft import msvc_runtime_flag
from conan.tools.files import rename
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.36.0"


class LibMysqlClientCConan(ConanFile):
    name = "libmysqlclient"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A MySQL client library for C development."
    topics = ("mysql", "sql", "connector", "database")
    homepage = "https://dev.mysql.com/downloads/mysql/"
    license = "GPL-2.0"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ssl": [True, False],
        "with_zlib": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssl": True,
        "with_zlib": True,
    }

    short_paths = True
    generators = "cmake", "pkg_config"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _with_zstd(self):
        return tools.Version(self.version) > "8.0.17"

    @property
    def _with_lz4(self):
        return tools.Version(self.version) > "8.0.17"

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16" if tools.Version(self.version) > "8.0.17" else "15",
            "gcc": "5.3",
            "clang": "6",
        }

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
        if self.options.with_ssl:
            self.requires("openssl/1.1.1m")
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self._with_zstd:
            self.requires("zstd/1.5.2")
        if self._with_lz4:
            self.requires("lz4/1.9.3")
        if self.settings.os == "FreeBSD":
            self.requires("libunwind/1.5.0")

    def validate(self):
        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and loose_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration("{} {} requires {} {} or newer".format(
                self.name, self.version, self.settings.compiler, minimum_version,
            ))

        if hasattr(self, "settings_build") and tools.cross_building(self, skip_x64_x86=True):
            raise ConanInvalidConfiguration("Cross compilation not yet supported by the recipe. contributions are welcome.")

        # FIXME: patch libmysqlclient 8.0.17 to support apple-clang >= 12?
        #        current errors:
        #             error: expected unqualified-id MYSQL_VERSION_MAJOR=8
        #             error: no member named 'ptrdiff_t' in the global namespace
        if self.version == "8.0.17" and self.settings.compiler == "apple-clang" and \
           tools.Version(self.settings.compiler.version) >= "12.0":
            raise ConanInvalidConfiguration("libmysqlclient 8.0.17 doesn't support apple-clang >= 12.0")

    def build_requirements(self):
        if tools.Version(self.version) >= "8.0.25" and tools.is_apple_os(self.settings.os):
            # CMake 3.18 or higher is required if Apple, but CI of CCI may run CMake 3.15
            self.build_requires("cmake/3.22.0")
        if self.settings.os == "FreeBSD":
            self.build_requires("pkgconf/1.7.4")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def _patch_files(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

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
        for folder in ["client", "man", "mysql-test", "libbinlogstandalone"]:
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

        # Do not copy shared libs of dependencies to package folder
        deps_shared = ["SSL"]
        if tools.Version(self.version) > "8.0.17":
            deps_shared.extend(["KERBEROS", "SASL", "LDAP", "PROTOBUF", "CURL"])
        for dep in deps_shared:
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                                  "MYSQL_CHECK_{}_DLLS()".format(dep),
                                  "")

        sources_cmake = os.path.join(self._source_subfolder, "CMakeLists.txt")
        sources_cmake_orig = os.path.join(self._source_subfolder, "CMakeListsOriginal.txt")
        rename(self, sources_cmake, sources_cmake_orig)
        rename(self, "CMakeLists.txt", sources_cmake)
        if self.settings.os == "Macos":
            tools.replace_in_file(os.path.join(self._source_subfolder, "libmysql", "CMakeLists.txt"),
                "COMMAND %s" % ("$<TARGET_FILE:libmysql_api_test>" if tools.Version(self.version) < "8.0.25" else "libmysql_api_test"),
                "COMMAND DYLD_LIBRARY_PATH=%s %s" %(os.path.join(self.build_folder, "library_output_directory"), os.path.join(self.build_folder, "runtime_output_directory", "libmysql_api_test")))
        tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "install_macros.cmake"),
            "  INSTALL_DEBUG_SYMBOLS(",
            "  # INSTALL_DEBUG_SYMBOLS(")

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["DISABLE_SHARED"] = not self.options.shared
        cmake.definitions["STACK_DIRECTION"] = "-1"  # stack grows downwards, on very few platforms stack grows upwards
        cmake.definitions["WITHOUT_SERVER"] = True
        cmake.definitions["WITH_UNIT_TESTS"] = False
        cmake.definitions["ENABLED_PROFILING"] = False
        cmake.definitions["WIX_DIR"] = False
        if self._with_lz4:
            cmake.definitions["WITH_LZ4"] = "system"

        if self._with_zstd:
            cmake.definitions["WITH_ZSTD"] = "system"
            cmake.definitions["ZSTD_INCLUDE_DIR"] = self.deps_cpp_info["zstd"].include_paths[0]

        if self._is_msvc:
            cmake.definitions["WINDOWS_RUNTIME_MD"] = "MD" in msvc_runtime_flag(self)

        if self.options.with_ssl:
            cmake.definitions["WITH_SSL"] = self.deps_cpp_info["openssl"].rootpath

        if self.options.with_zlib:
            cmake.definitions["WITH_ZLIB"] = "system"
        cmake.configure(source_dir=self._source_subfolder)
        return cmake

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
        rename(self, os.path.join(self.package_folder, "LICENSE"), os.path.join(self.package_folder, "licenses", "LICENSE"))
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
        self.cpp_info.set_property("pkg_config_name", "mysqlclient")
        self.cpp_info.names["pkg_config"] = "mysqlclient"
        self.cpp_info.libs = ["libmysql" if self.settings.os == "Windows" and self.options.shared else "mysqlclient"]
        if not self.options.shared:
            stdcpp_library = tools.stdcpp_library(self)
            if stdcpp_library:
                self.cpp_info.system_libs.append(stdcpp_library)
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.append("m")

        # TODO: There is no official FindMySQL.cmake, but it's a common Find files in many projects
        #       do we want to support it in CMakeDeps?
        self.cpp_info.names["cmake_find_package"] = "MySQL"
        self.cpp_info.names["cmake_find_package_multi"] = "MySQL"
