import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.files import get, replace_in_file, copy, rm
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime

required_conan_version = ">=1.64.1"

class MysqlCppConnRecipe(ConanFile):
    name = "mysql-connector-cpp"
    package_type = "library"
    short_paths = True
    version= "9.0.0"

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
        self.requires("openssl/1.0.2u")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("protobuf/3.21.12")

    def build_requirements(self):
        if not is_msvc(self):
            self.tool_requires("ninja/[>=1.10 <2]")

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

    def _package_folder_dep(self, dep):
        return self.dependencies[dep].package_folder.replace("\\", "/")

    def _include_folder_dep(self, dep):
        return self.dependencies[dep].cpp_info.includedirs[0].replace("\\", "/")

    def _lib_folder_dep(self, dep):
        return self.dependencies[dep].cpp_info.libdirs[0].replace("\\", "/")

    def generate(self):

        tc = CMakeToolchain(self, generator="Ninja") if not is_msvc(self) else CMakeToolchain(self)

        # OpenSSL
        tc.cache_variables["WITH_SSL"] = "SYSTEM"
        # LZ4 patches
        tc.cache_variables["WITH_LZ4"] = "TRUE"
        # ZLIB patches
        tc.cache_variables["WITH_ZLIB"] = "TRUE" if self.settings.os == "Windows" else self._package_folder_dep("zlib")
        # ZSTD patches
        tc.cache_variables["WITH_ZSTD"] = "TRUE"
        # Build patches
        tc.cache_variables["BUILD_STATIC"] = not self.options.shared
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        # Disable Boost, only legacy JDBC connector needs it
        tc.cache_variables["BOOST_DIR"] = "FALSE"
        # Protobuf
        tc.cache_variables["WITH_PROTOBUF"] = self._package_folder_dep("protobuf")

        # Windows patches
        if self.settings.os == "Windows":
            # OpenSSL patches
            tc.cache_variables["WITH_SSL"] = self._package_folder_dep("openssl")

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):

        # Fix static lib naming
        if not self.options.shared and is_msvc(self):
            replace_in_file(self, os.path.join(self.source_folder, "install_layout.cmake"),
                                "set(LIB_NAME_STATIC \"${LIB_NAME}-mt\")",
                                "set(LIB_NAME_STATIC \"${LIB_NAME_STATIC}-mt\")",
                                strict=False)

        # ZSTD patch
        replace_in_file(self, os.path.join(self.source_folder, "cdk", "extra", "zstd", "CMakeLists.txt"),
                            "enable_pic()",
                            "enable_pic()\n"\
                            "add_compile_definitions(ZSTD_DISABLE_ASM)",
                            strict=False)

        # Fix shared zlib build = duplicate references
        if self.options.shared and self.settings.os in ["Linux", "FreeBSD"] :
            # ZLIB patch
            replace_in_file(self, os.path.join(self.source_folder, "cdk", "extra", "protobuf", "protobuf-3.19.6", "cmake", "CMakeLists.txt"),
                                "set(protobuf_WITH_ZLIB_DEFAULT ON)",
                                "set(protobuf_WITH_ZLIB_DEFAULT OFF)",
                                strict=False)

            # mysqlx && ZLIB patch
            replace_in_file(self, os.path.join(self.source_folder, "cdk", "protocol", "mysqlx", "CMakeLists.txt"),
                                "PRIVATE cdk_foundation ext::z ext::lz4 ext::zstd",
                                "PRIVATE cdk_foundation ZLIB::ZLIB ext::lz4 ext::zstd",
                                strict=False)

        # Apple patches
        if is_apple_os(self) and cross_building(self):
            patch = f"set(CMAKE_OSX_ARCHITECTURES \"{self.settings.arch}\" CACHE INTERNAL \"\" FORCE)\n"

            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                                "PROJECT(MySQL_CONCPP)",
                                f"PROJECT(MySQL_CONCPP)\n{patch}",
                                strict=False)
            # Packages-Apple patches
            for lb in ["lz4", 'zlib', 'protobuf', 'zstd']:
                replace_in_file(self, os.path.join(self.source_folder, "cdk", "extra", lb, "CMakeLists.txt"),
                                    "enable_pic()",
                                    f"enable_pic()\n{patch}",
                                    strict=False)

        # Protobuf patches
        protobuf = "protobufd" if self.dependencies["protobuf"].settings.build_type == "Debug" else "protobuf"
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

    @property
    def _package_dirs(self):
        template_dirs = ["lib64", "lib"] if self.settings.build_type == "Release" else  [os.path.join("lib64", "debug"), os.path.join("lib", "debug")]
        if is_msvc(self):
            template_dirs = [os.path.join(lib, "vs14") for lib in template_dirs]
        else:
            template_dirs = template_dirs

        # Clean out bad dirs
        template_dirs = [path for path in template_dirs if os.path.isdir(path)]
        return template_dirs

    def package_info(self):
        dirs = self._package_dirs
        self.cpp_info.bindirs = dirs
        self.cpp_info.libdirs= dirs

        if is_apple_os(self) or self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["resolv"])
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.extend(["m", "pthread"])

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
