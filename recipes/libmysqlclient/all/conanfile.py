from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import cross_building, stdcpp_library
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import rename, get, apply_conandata_patches, replace_in_file, rmdir, rm, export_conandata_patches, copy, mkdir
from conan.tools.microsoft import is_msvc, msvc_runtime_flag
from conan.tools.scm import Version
import os

required_conan_version = ">=1.56.0"


class LibMysqlClientCConan(ConanFile):
    name = "libmysqlclient"
    description = "A MySQL client library for C development."
    license = "GPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("mysql", "sql", "connector", "database")
    homepage = "https://dev.mysql.com/downloads/mysql/"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }
    package_type = "library"
    short_paths = True
    generators = "PkgConfigDeps"

    def layout(self):
        cmake_layout(self, src_folder="src")

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16" if Version(self.version) > "8.0.17" else "15",
            "gcc": "7" if Version(self.version) >= "8.0.27" else "5.3",
            "clang": "6",
        }

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("openssl/1.1.1s")
        self.requires("zlib/1.2.13")
        self.requires("zstd/1.5.2")
        self.requires("lz4/1.9.4")
        if self.settings.os == "FreeBSD":
            self.requires("libunwind/1.6.2")

    def validate(self):
        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and loose_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(f"{self.name} {self.version} requires {self.settings.compiler} {minimum_version} or newer")

        if hasattr(self, "settings_build") and cross_building(self, skip_x64_x86=True):
            raise ConanInvalidConfiguration("Cross compilation not yet supported by the recipe. Contributions are welcomed.")

        # FIXME: patch libmysqlclient 8.0.17 to support apple-clang >= 12?
        #        current errors:
        #             error: expected unqualified-id MYSQL_VERSION_MAJOR=8
        #             error: no member named 'ptrdiff_t' in the global namespace
        if self.version == "8.0.17" and self.settings.compiler == "apple-clang" and \
                Version(self.settings.compiler.version) >= "12.0":
            raise ConanInvalidConfiguration("libmysqlclient 8.0.17 doesn't support apple-clang >= 12.0")

        # mysql>=8.0.17 doesn't support shared library on MacOS.
        # https://github.com/mysql/mysql-server/blob/mysql-8.0.17/cmake/libutils.cmake#L333-L335
        if Version(self.version) >= "8.0.17" and self.settings.compiler == "apple-clang" and \
                self.options.shared:
            raise ConanInvalidConfiguration(f"{self.name}/{self.version} doesn't support shared library")

        # mysql < 8.0.29 uses `requires` in source code. It is the reserved keyword in C++20.
        # https://github.com/mysql/mysql-server/blob/mysql-8.0.0/include/mysql/components/services/dynamic_loader.h#L270
        if self.settings.compiler.get_safe("cppstd") == "20" and Version(self.version) < "8.0.29":
            raise ConanInvalidConfiguration(f"{self.name}/{self.version} doesn't support C++20")

    def _cmake_new_enough(self, required_version):
        try:
            import re
            from io import StringIO
            output = StringIO()
            self.run("cmake --version", output)
            m = re.search(r'cmake version (\d+\.\d+\.\d+)', output.getvalue())
            return Version(m.group(1)) >= required_version
        except:
            return False

    def build_requirements(self):
        if Version(self.version) >= "8.0.25" and is_apple_os(self) and not self._cmake_new_enough("3.18"):
            # CMake 3.18 or higher is required if Apple, but CI of CCI may run CMake 3.15
            # Set it to 3.24 as that matches our openssl version too
            self.tool_requires("cmake/3.24.2")
        if self.settings.os == "FreeBSD":
            self.tool_requires("pkgconf/1.9.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def _patch_files(self):
        apply_conandata_patches(self)

        libs_to_remove = ["icu", "libevent", "re2", "rapidjson", "protobuf", "libedit"]
        for lib in libs_to_remove:
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            f"MYSQL_CHECK_{lib.upper()}()\n",
                            "",
                            strict=False)
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            f"INCLUDE({lib})\n",
                            "",
                            strict=False)
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            f"WARN_MISSING_SYSTEM_{lib.upper()}({lib.upper()}_WARN_GIVEN)",
                            f"# WARN_MISSING_SYSTEM_{lib.upper()}({lib.upper()}_WARN_GIVEN)",
                            strict=False)

            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            f"SET({lib.upper()}_WARN_GIVEN)",
                            f"# SET({lib.upper()}_WARN_GIVEN)",
                            strict=False)

        rmdir(self, os.path.join(self.source_folder, "extra"))
        for folder in ["client", "man", "mysql-test", "libbinlogstandalone"]:
            rmdir(self, os.path.join(self.source_folder, folder))
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            f"ADD_SUBDIRECTORY({folder})\n",
                            "",
                            strict=False)
        rmdir(self, os.path.join(self.source_folder, "storage", "ndb"))
        for t in ["INCLUDE(cmake/boost.cmake)\n", "MYSQL_CHECK_EDITLINE()\n"]:
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            t,
                            "",
                            strict=False)

        # Upstream does not actually load lz4 directories for system, force it to
        replace_in_file(self, os.path.join(self.source_folder, "libbinlogevents", "CMakeLists.txt"),
                        "INCLUDE_DIRECTORIES(${CMAKE_SOURCE_DIR}/libbinlogevents/include)",
                        "MY_INCLUDE_SYSTEM_DIRECTORIES(LZ4)\nINCLUDE_DIRECTORIES(${CMAKE_SOURCE_DIR}/libbinlogevents/include)")

        replace_in_file(self, os.path.join(self.source_folder, "cmake", "zstd.cmake"),
                        "NAMES zstd",
                        f"NAMES zstd {self.dependencies['zstd'].cpp_info.components['zstdlib'].libs[0]}")

        replace_in_file(self, os.path.join(self.source_folder, "cmake", "ssl.cmake"),
                        "NAMES ssl",
                        f"NAMES ssl {self.dependencies['openssl'].cpp_info.components['ssl'].libs[0]}")

        replace_in_file(self, os.path.join(self.source_folder, "cmake", "ssl.cmake"),
                        "NAMES crypto",
                        f"NAMES crypto {self.dependencies['openssl'].cpp_info.components['crypto'].libs[0]}")

        replace_in_file(self, os.path.join(self.source_folder, "cmake", "ssl.cmake"),
                        "IF(NOT OPENSSL_APPLINK_C)\n",
                        "IF(FALSE AND NOT OPENSSL_APPLINK_C)\n",
                        strict=False)

        # Do not copy shared libs of dependencies to package folder
        deps_shared = ["SSL"]
        if Version(self.version) > "8.0.17":
            deps_shared.extend(["KERBEROS", "SASL", "LDAP", "PROTOBUF", "CURL"])
        for dep in deps_shared:
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            f"MYSQL_CHECK_{dep}_DLLS()",
                            "")

        if self.settings.os == "Macos":
            replace_in_file(self, os.path.join(self.source_folder, "libmysql", "CMakeLists.txt"),
                            f"COMMAND {'$<TARGET_FILE:libmysql_api_test>' if Version(self.version) < '8.0.25' else 'libmysql_api_test'}",
                            f"COMMAND DYLD_LIBRARY_PATH={os.path.join(self.build_folder, 'library_output_directory')} {os.path.join(self.build_folder, 'runtime_output_directory', 'libmysql_api_test')}")
        replace_in_file(self, os.path.join(self.source_folder, "cmake", "install_macros.cmake"),
                        "  INSTALL_DEBUG_SYMBOLS(",
                        "  # INSTALL_DEBUG_SYMBOLS(")

    def generate(self):
        cmake = CMakeToolchain(self)
        # Not used anywhere in the CMakeLists

        cmake.cache_variables["DISABLE_SHARED"] = not self.options.shared
        cmake.cache_variables["STACK_DIRECTION"] = "-1"  # stack grows downwards, on very few platforms stack grows upwards
        cmake.cache_variables["WITHOUT_SERVER"] = True
        cmake.cache_variables["WITH_UNIT_TESTS"] = False
        cmake.cache_variables["ENABLED_PROFILING"] = False
        cmake.cache_variables["MYSQL_MAINTAINER_MODE"] = False
        cmake.cache_variables["WIX_DIR"] = False

        cmake.cache_variables["WITH_LZ4"] = "system"

        cmake.cache_variables["WITH_ZSTD"] = "system"
        cmake.cache_variables["ZSTD_INCLUDE_DIR"] = self.dependencies["zstd"].cpp_info.includedirs[0]

        if is_msvc(self):
            cmake.cache_variables["WINDOWS_RUNTIME_MD"] = "MD" in msvc_runtime_flag(self)

        cmake.cache_variables["WITH_SSL"] = self.dependencies["openssl"].package_folder

        cmake.cache_variables["WITH_ZLIB"] = "system"
        cmake.generate()

    def build(self):
        self._patch_files()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        mkdir(self, os.path.join(self.package_folder, "licenses"))
        rename(self, os.path.join(self.package_folder, "LICENSE"), os.path.join(self.package_folder, "licenses", "LICENSE"))
        rm(self, "README", self.package_folder)
        rm(self, "*.pdb", self.package_folder, recursive=True)
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "docs"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        if self.settings.os == "Windows" and self.options.shared:
            copy(self, "*.dll", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        if self.options.shared:
            rm(self, "*.a", self.package_folder, recursive=True)
        else:
            rm(self, "*.dll", self.package_folder, recursive=True)
            rm(self, "*.dylib", self.package_folder, recursive=True)
            rm(self, "*.so*", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "mysqlclient")
        self.cpp_info.names["pkg_config"] = "mysqlclient"
        self.cpp_info.libs = ["libmysql" if self.settings.os == "Windows" and self.options.shared else "mysqlclient"]
        if not self.options.shared:
            stdcpplib = stdcpp_library(self)
            if stdcpplib:
                self.cpp_info.system_libs.append(stdcpplib)
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.append("m")
        if self.settings.os in ["Linux", "FreeBSD"]:
            if Version(self.version) >= "8.0.25":
                self.cpp_info.system_libs.append("resolv")
        if self.settings.os == "Windows":
            if Version(self.version) >= "8.0.25":
                self.cpp_info.system_libs.append("dnsapi")
            self.cpp_info.system_libs.append("secur32")

        # TODO: There is no official FindMySQL.cmake, but it's a common Find files in many projects
        #       do we want to support it in CMakeDeps?
        self.cpp_info.names["cmake_find_package"] = "MySQL"
        self.cpp_info.names["cmake_find_package_multi"] = "MySQL"
