from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, cross_building, stdcpp_library
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.env import VirtualRunEnv, VirtualBuildEnv
from conan.tools.files import rename, get, apply_conandata_patches, replace_in_file, rmdir, rm, export_conandata_patches, mkdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=1.55.0"


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
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    package_type = "library"
    short_paths = True

    @property
    def _min_cppstd(self):
        return "17" if Version(self.version) >= "8.0.27" else "11"

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "7" if Version(self.version) >= "8.0.27" else "5.3",
            "clang": "6",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if Version(self.version) < "8.0.30":
            self.requires("openssl/1.1.1w")
        else:
            self.requires("openssl/[>=1.1 <4]")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("zstd/1.5.5")
        self.requires("lz4/1.9.4")
        if self.settings.os == "FreeBSD":
            self.requires("libunwind/1.7.2")

    def validate_build(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        if hasattr(self, "settings_build") and cross_building(self, skip_x64_x86=True):
            raise ConanInvalidConfiguration("Cross compilation not yet supported by the recipe. Contributions are welcomed.")

    def validate(self):
        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and loose_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(f"{self.ref} requires {self.settings.compiler} {minimum_version} or newer")

        # mysql < 8.0.29 uses `requires` in source code. It is the reserved keyword in C++20.
        # https://github.com/mysql/mysql-server/blob/mysql-8.0.0/include/mysql/components/services/dynamic_loader.h#L270
        if self.settings.compiler.get_safe("cppstd") == "20" and Version(self.version) < "8.0.29":
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support C++20")

    def build_requirements(self):
        if is_apple_os(self):
            self.tool_requires("cmake/[>=3.18 <4]")
        if self.settings.os == "FreeBSD" and not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.0.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _patch_sources(self):
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

            if lib != "libevent" or Version(self.version) < "8.0.34":
                replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                                f"SET({lib.upper()}_WARN_GIVEN)",
                                f"# SET({lib.upper()}_WARN_GIVEN)",
                                strict=False)

        for folder in ["client", "man", "mysql-test", "libbinlogstandalone"]:
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
        if Version(self.version) < "8.0.34":
            replace_in_file(self, os.path.join(self.source_folder, "libbinlogevents", "CMakeLists.txt"),
                            "INCLUDE_DIRECTORIES(${CMAKE_SOURCE_DIR}/libbinlogevents/include)",
                            "MY_INCLUDE_SYSTEM_DIRECTORIES(LZ4)\nINCLUDE_DIRECTORIES(${CMAKE_SOURCE_DIR}/libbinlogevents/include)")

        replace_in_file(self, os.path.join(self.source_folder, "cmake", "zstd.cmake"),
                        "NAMES zstd",
                        f"NAMES zstd {self.dependencies['zstd'].cpp_info.aggregated_components().libs[0]}")

        # Fix discovery & link to OpenSSL
        ssl_cmake = os.path.join(self.source_folder, "cmake", "ssl.cmake")
        replace_in_file(self, ssl_cmake,
                        "NAMES ssl",
                        f"NAMES ssl {self.dependencies['openssl'].cpp_info.components['ssl'].libs[0]}")

        replace_in_file(self, ssl_cmake,
                        "NAMES crypto",
                        f"NAMES crypto {self.dependencies['openssl'].cpp_info.components['crypto'].libs[0]}")

        replace_in_file(self, ssl_cmake,
                        "IF(NOT OPENSSL_APPLINK_C)\n",
                        "IF(FALSE AND NOT OPENSSL_APPLINK_C)\n",
                        strict=False)

        replace_in_file(self, ssl_cmake,
                        "SET(SSL_LIBRARIES ${MY_OPENSSL_LIBRARY} ${MY_CRYPTO_LIBRARY})",
                        "find_package(OpenSSL REQUIRED MODULE)\nset(SSL_LIBRARIES OpenSSL::SSL OpenSSL::Crypto)")

        # And do not merge OpenSSL libs into mysqlclient lib
        replace_in_file(self, os.path.join(self.source_folder, "cmake", "libutils.cmake"),
                        'IF(WIN32 AND ${TARGET} STREQUAL "mysqlclient")',
                        "if(0)")

        # Do not copy shared libs of dependencies to package folder
        deps_shared = ["SSL", "KERBEROS", "SASL", "LDAP", "PROTOBUF"]
        if Version(self.version) < "8.0.34":
            deps_shared.append("CURL")
        for dep in deps_shared:
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            f"MYSQL_CHECK_{dep}_DLLS()",
                            "")

        if self.settings.os == "Macos":
            replace_in_file(self, os.path.join(self.source_folder, "libmysql", "CMakeLists.txt"),
                            f"COMMAND {'libmysql_api_test'}",
                            f"COMMAND DYLD_LIBRARY_PATH={os.path.join(self.build_folder, 'library_output_directory')} {os.path.join(self.build_folder, 'runtime_output_directory', 'libmysql_api_test')}")
        replace_in_file(self, os.path.join(self.source_folder, "cmake", "install_macros.cmake"),
                        "  INSTALL_DEBUG_SYMBOLS(",
                        "  # INSTALL_DEBUG_SYMBOLS(")

    def generate(self):
        vbenv = VirtualBuildEnv(self)
        vbenv.generate()

        if not cross_building(self):
            vrenv = VirtualRunEnv(self)
            vrenv.generate(scope="build")

        tc = CMakeToolchain(self)
        # Not used anywhere in the CMakeLists
        tc.cache_variables["DISABLE_SHARED"] = not self.options.shared
        tc.cache_variables["STACK_DIRECTION"] = "-1"  # stack grows downwards, on very few platforms stack grows upwards
        tc.cache_variables["WITHOUT_SERVER"] = True
        tc.cache_variables["WITH_UNIT_TESTS"] = False
        tc.cache_variables["ENABLED_PROFILING"] = False
        tc.cache_variables["MYSQL_MAINTAINER_MODE"] = False
        tc.cache_variables["WIX_DIR"] = False
        # Disable additional Linux distro-specific compiler checks.
        # The recipe already checks for minimum versions of supported
        # compilers.
        tc.cache_variables["FORCE_UNSUPPORTED_COMPILER"] = True

        tc.cache_variables["WITH_LZ4"] = "system"

        tc.cache_variables["WITH_ZSTD"] = "system"
        tc.cache_variables["ZSTD_INCLUDE_DIR"] = self.dependencies["zstd"].cpp_info.aggregated_components().includedirs[0].replace("\\", "/")

        if is_msvc(self):
            tc.cache_variables["WINDOWS_RUNTIME_MD"] = not is_msvc_static_runtime(self)

        tc.cache_variables["WITH_SSL"] = self.dependencies["openssl"].package_folder.replace("\\", "/")

        tc.cache_variables["WITH_ZLIB"] = "system"

        # Remove to ensure reproducible build, this only affects docs generation
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Doxygen"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

        if self.settings.os == "FreeBSD":
            deps = PkgConfigDeps(self)
            deps.generate()

    def build(self):
        self._patch_sources()
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
        rmdir(self, os.path.join(self.package_folder, "lib", "plugin"))
        rmdir(self, os.path.join(self.package_folder, "docs"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        if self.settings.os == "Windows":
            if self.options.shared:
                rename(self, os.path.join(self.package_folder, "lib", "libmysql.dll"),
                             os.path.join(self.package_folder, "bin", "libmysql.dll"))
                rm(self, "*mysqlclient.*", os.path.join(self.package_folder, "lib"))
            else:
                rm(self, "*.dll", os.path.join(self.package_folder, "lib"))
                rm(self, "*libmysql.*", os.path.join(self.package_folder, "lib"))
        else:
            if self.options.shared:
                rm(self, "*.a", os.path.join(self.package_folder, "lib"))
            else:
                rm(self, "*.dylib", os.path.join(self.package_folder, "lib"))
                rm(self, "*.so*", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "mysqlclient")
        self.cpp_info.libs = ["libmysql" if self.settings.os == "Windows" and self.options.shared else "mysqlclient"]
        self.cpp_info.includedirs.append(os.path.join("include", "mysql"))
        if not self.options.shared:
            stdcpplib = stdcpp_library(self)
            if stdcpplib:
                self.cpp_info.system_libs.append(stdcpplib)
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.extend(["m", "resolv"])
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["dnsapi", "secur32"])

        # TODO: There is no official FindMySQL.cmake, but it's a common Find files in many projects
        #       do we want to support it in CMakeDeps?
        self.cpp_info.names["cmake_find_package"] = "MySQL"
        self.cpp_info.names["cmake_find_package_multi"] = "MySQL"
