import os
import shutil
from conan import ConanFile
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.files import get, replace_in_file, copy, rm, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime

required_conan_version = ">=1.64.1"

class MysqlCppConnRecipe(ConanFile):
    name = "mysql-connector-cpp"
    package_type = "library"
    short_paths = True
    version = "9.0.0"

    # Optional metadata
    license = "GPL-2.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mysql/mysql-connector-cpp"
    description = "A MySQL client library for C++ development"
    topics = ("mysql", "sql", "connector", "database", "c++", "cpp")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {
               "shared": [True, False],
               "fPIC": [True, False],
               }

    default_options = { "shared": False, "fPIC": True }

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "14",
            "msvc": "192",
            "gcc": "8",
            "clang": "7",
            "apple-clang": "10",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "17")

        # Compiler minimum version
        compiler = self.settings.compiler
        compiler_name = str(compiler)
        minimum_version = self._minimum_compilers_version.get(compiler_name, False)
        if minimum_version and Version(compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"Requires compiler {compiler_name} minimum version: {minimum_version} with C++17 support."
            )

    def requirements(self):
        self.requires("openssl/[>=1.1 <4]")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("zstd/[>=1.5 <1.6]")
        self.requires("lz4/[>=1.9.2 <=1.10.0]")
        self.requires("protobuf/3.21.12")
        self.requires("rapidjson/1.1.0")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.24 <4]")
        self.tool_requires("protobuf/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def _package_folder_dep(self, dep, scope="host"):
        try:
            if scope == "build":
                return self.dependencies.build[dep].package_folder.replace("\\", "/")
        except:
            self.output.info(f"Failed to get a build scoped package path for : {dep}")
        return self.dependencies[dep].package_folder.replace("\\", "/")

    def _include_folder_dep(self, dep):
        return self.dependencies[dep].cpp_info.includedirs[0].replace("\\", "/")

    def _lib_folder_dep(self, dep):
        return self.dependencies[dep].cpp_info.libdirs[0].replace("\\", "/")

    def generate(self):

        tc = CMakeToolchain(self)

        # OpenSSL
        tc.cache_variables["WITH_SSL"] = self._package_folder_dep("openssl")
        tc.cache_variables["OPENSSL_ROOT_DIR"] = self._package_folder_dep("openssl")
        # LZ4 patches
        tc.cache_variables["WITH_LZ4"] = self._package_folder_dep("lz4")
        # ZLIB patches
        tc.cache_variables["WITH_ZLIB"] = self._package_folder_dep("zlib")
        # ZSTD patches
        tc.cache_variables["WITH_ZSTD"] = self._package_folder_dep("zstd")
        # Build patches
        tc.cache_variables["BUILD_STATIC"] = not self.options.shared
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        # Disable Boost, only legacy JDBC connector needs it
        tc.cache_variables["BOOST_DIR"] = "FALSE"
        # Protobuf
        tc.cache_variables["WITH_PROTOBUF"] = self._package_folder_dep("protobuf")
        # RapidJSON
        tc.cache_variables["RAPIDJSON_INCLUDE_DIR"] = self._include_folder_dep("rapidjson")

        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("protobuf::libprotobuf", "cmake_target_name", "ext::protobuf")
        deps.set_property("protobuf::libprotobuf-lite", "cmake_target_name", "ext::protobuf-lite")
        deps.set_property("rapidjson", "cmake_target_name", "RapidJSON::rapidjson")
        deps.set_property("zlib", "cmake_target_name", "ext::z")
        deps.set_property("lz4", "cmake_target_name", "ext::lz4")
        deps.set_property("zstd", "cmake_target_name", "ext::zstd")
        deps.generate()

    def _patch_sources(self):

        # Delete internal libs
        rmdir(self, os.path.join(self.source_folder, "cdk", "extra"))
        rm(self, "DepFindSSL.cmake", os.path.join(self.source_folder, "cdk", "cmake"))

        # Fix static lib naming
        if not self.options.shared and is_msvc(self):
            replace_in_file(self, os.path.join(self.source_folder, "install_layout.cmake"),
                                "set(LIB_NAME_STATIC \"${LIB_NAME}-mt\")",
                                "set(LIB_NAME_STATIC \"${LIB_NAME_STATIC}-mt\")",
                                strict=False)

        # Apple patches
        if is_apple_os(self) and cross_building(self):
            patch = f"set(CMAKE_OSX_ARCHITECTURES \"{self.settings.arch}\" CACHE INTERNAL \"\" FORCE)\n"
            # Package level
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "PROJECT(MySQL_CONCPP)", f"PROJECT(MySQL_CONCPP)\n{patch}", strict=False)

        # ZLIB patch
        zlib_name = "z" if not self.settings.os == "Windows" else "zlib"
        replace_in_file(self, os.path.join(self.source_folder, "cdk", "cmake", "DepFindCompression.cmake"), "add_ext(zlib zlib.h z ext_zlib)", f"add_ext(zlib zlib.h {zlib_name} ext_zlib)")

        # ZSTD patch
        zstd_name = "zstd" if not self.settings.os == "Windows" else "zstd_static"
        replace_in_file(self, os.path.join(self.source_folder, "cdk", "cmake", "DepFindCompression.cmake"), "add_ext(zstd zstd.h zstd ext_zstd)", f"add_ext(zstd zstd.h {zstd_name} ext_zstd)")

        # Compression patch
        replace_in_file(self, os.path.join(self.source_folder, "cdk", "protocol", "mysqlx","CMakeLists.txt"), "PRIVATE cdk_foundation ext::z ext::lz4 ext::zstd", f"PRIVATE cdk_foundation ext::{zlib_name} ext::lz4 ext::{zstd_name}")

        # OpenSSL patch
        replace_in_file(self, os.path.join(self.source_folder, "mysql-concpp-config.cmake.in"), "find_deps()", "")
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "find_dependency(SSL)", "")
        # Remove problematic func
        # replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "bootstrap()", "#bootstrap()")
        # cdk target
        replace_in_file(self, os.path.join(self.source_folder, "cdk", "CMakeLists.txt"), "find_dependency(SSL)", "")
        replace_in_file(self, os.path.join(self.source_folder, "cdk", "CMakeLists.txt"), "ADD_SUBDIRECTORY(extra)", "")
        # foundation target
        replace_in_file(self, os.path.join(self.source_folder, "cdk", "foundation", "CMakeLists.txt"), "include(CheckCXXSourceCompiles)", "find_package(OpenSSL REQUIRED)")
        extra_lib = "Crypt32" if self.settings.os == "Windows" else ""
        replace_in_file(self, os.path.join(self.source_folder, "cdk", "foundation", "CMakeLists.txt"), "# generated config.h", "\"${RAPIDJSON_INCLUDE_DIR}\"")
        replace_in_file(self, os.path.join(self.source_folder, "cdk", "foundation", "CMakeLists.txt"), "PRIVATE OpenSSL::SSL", f"OpenSSL::SSL {extra_lib}")
        # mysqlx target
        replace_in_file(self, os.path.join(self.source_folder, "cdk", "mysqlx", "CMakeLists.txt"),
                        "target_link_libraries(cdk_mysqlx PUBLIC cdk_proto_mysqlx cdk_foundation)",
                        "target_link_libraries(cdk_mysqlx PUBLIC cdk_foundation cdk_proto_mysqlx)")
        replace_in_file(self, os.path.join(self.source_folder, "cdk", "mysqlx", "CMakeLists.txt"), "target_link_libraries(cdk_mysqlx PRIVATE OpenSSL::SSL)", "")

        # Protobuf patches
        try:
            protobuf = "protobufd" if self.dependencies.build["protobuf"].settings.build_type == "Debug" else "protobuf"
        except:
            protobuf = "protobuf"
        # INFO: Disable protobuf-lite to use Conan protobuf targets instead
        replace_in_file(self, os.path.join(self.source_folder, "cdk", "cmake", "DepFindProtobuf.cmake"), "LIBRARY protobuf-lite pb_libprotobuf-lite", "")
        # INFO: Fix protobuf library name according to the build type
        replace_in_file(self, os.path.join(self.source_folder, "cdk", "cmake", "DepFindProtobuf.cmake"), "LIBRARY protobuf", f"LIBRARY {protobuf}")
        # INFO: Disable protobuf-lite to use Conan protobuf targets instead
        replace_in_file(self, os.path.join(self.source_folder, "cdk", "protocol", "mysqlx", "CMakeLists.txt"), "ext::protobuf-lite", f"ext::{protobuf}")
        # INFO: Disable protobuf-lite to use Conan protobuf targets instead
        replace_in_file(self, os.path.join(self.source_folder, "cdk", "core", "CMakeLists.txt"), "ext::protobuf-lite", f"ext::{protobuf}")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        # Clean
        rm(self, "INFO_SRC", self.package_folder)
        rm(self, "INFO_BIN", self.package_folder)
        rm(self, "*.cmake", self.package_folder)

        # Add License
        copy(self, "LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

        # Just rename the lib64 dir
        source_dir = os.path.join(self.package_folder, "lib64")
        if os.path.isdir(source_dir):
            shutil.move(source_dir, os.path.join(self.package_folder, "lib"))

    def package_info(self):

        # Lib dir
        lib_dir = "lib" if self.settings.build_type == "Release" else os.path.join("lib", "debug")
        if is_msvc(self):
            lib_dir = [os.path.join(lib_dir, "vs14")]
        else:
            lib_dir = [lib_dir]
        self.cpp_info.libdirs = lib_dir
        self.cpp_info.bindirs = ["lib"]

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["dnsapi", "ws2_32"])
        if is_apple_os(self) or self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["resolv"])
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.extend(["m", "pthread", "dl"])

        target = "concpp-xdevapi"
        target_alias = "concpp"

        if self.options.shared:
            target += "-static"
            target_alias += "-static"

        if self.settings.build_type == "Debug":
            target += "-debug"
            target_alias += "-debug"

        self.cpp_info.set_property("cmake_target_name", "mysql::concpp")
        self.cpp_info.set_property("cmake_target_aliases", [f"mysql::{target_alias}"] )

        lib = "mysqlcppconnx" if self.options.shared else "mysqlcppconnx-static"
        if is_msvc(self) and not self.options.shared and is_msvc_static_runtime(self):
            lib += "-mt"
        self.cpp_info.libs = [lib]

        if not self.options.shared:
            self.cpp_info.defines = ["MYSQL_STATIC"]
            self.cpp_info.defines = ["STATIC_CONCPP"]
