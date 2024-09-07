import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import get, copy, rm, export_conandata_patches, apply_conandata_patches, replace_in_file
from conan.tools.microsoft import is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=1.55.0"


class MysqlConnectorCppConan(ConanFile):
    name = "mysql-connector-cpp"
    description = "MySQL database connector for C++ applications"
    license = "GPL-2.0-only WITH Universal-FOSS-exception-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://dev.mysql.com/doc/connector-cpp/en/"
    topics = ("mysql", "sql", "connector", "database")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "8",
            "clang": "7",
            "apple-clang": "10",
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
        # None of the dependencies are used transitively
        self.requires("protobuf/3.21.12")  # v4 and newer are not supported as of v9.0.0
        self.requires("openssl/[>=1.1 <4]")
        self.requires("rapidjson/1.1.0")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("lz4/1.9.4")
        self.requires("zstd/[~1.5]")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires {self.settings.compiler} {minimum_version} or newer")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.24 <4]")
        self.tool_requires("protobuf/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()
        if self.dependencies["protobuf"].options.shared:
            VirtualRunEnv(self).generate(scope="build")

        tc = CMakeToolchain(self)
        tc.cache_variables["BUNDLE_DEPENDENCIES"] = False
        tc.cache_variables["BUILD_STATIC"] = not self.options.shared
        tc.cache_variables["STATIC_MSVCRT"] = is_msvc_static_runtime(self)
        tc.cache_variables["WITH_TESTS"] = False
        tc.cache_variables["CMAKE_TRY_COMPILE_CONFIGURATION"] = str(self.settings.build_type)
        tc.cache_variables["WITH_SSL"] = self.dependencies["openssl"].package_folder.replace("\\", "/")
        tc.cache_variables["CMAKE_PREFIX_PATH"] = self.generators_folder.replace("\\", "/")
        tc.cache_variables["IS64BIT"] = True
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
        apply_conandata_patches(self)
        if is_apple_os(self):
            # The CMAKE_OSX_ARCHITECTURES value set by Conan seems to be having no effect for some reason.
            # This is a workaround for that.
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            "PROJECT(MySQL_CONCPP)",
                            f"PROJECT(MySQL_CONCPP)\n\nadd_compile_options(-arch {self.settings.arch})\n")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rm(self, "INFO_SRC", self.package_folder)
        rm(self, "INFO_BIN", self.package_folder)
        rm(self, "*.cmake", self.package_folder)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "mysql-concpp")
        self.cpp_info.set_property("cmake_target_name", "mysql::concpp")

        aliases = ["mysql::concpp-xdevapi"]
        if not self.options.shared:
            aliases.append("mysql::concpp-static")
            aliases.append("mysql::concpp-xdevapi-static")
            if self.settings.build_type == "Debug":
                aliases.append("mysql::concpp-static-debug")
                aliases.append("mysql::concpp-xdevapi-static-debug")
        aliases.append("mysql::openssl")
        self.cpp_info.set_property("cmake_target_aliases", aliases)

        lib = "mysqlcppconnx"
        if not self.options.shared:
            lib += "-static"
            if is_msvc_static_runtime(self):
                lib += "-mt"
        self.cpp_info.libs = [lib]

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("dnsapi")
            self.cpp_info.system_libs.append("ws2_32")
        elif self.settings.os != "FreeBSD":
            self.cpp_info.system_libs.append("resolv")
        if self.settings.os == "SunOS":
            self.cpp_info.system_libs.append("socket")
            self.cpp_info.system_libs.append("nsl")

        if not self.options.shared:
            self.cpp_info.defines = ["MYSQL_STATIC", "STATIC_CONCPP"]


        if is_apple_os(self) or self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["resolv"])
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.extend(["m", "pthread"])