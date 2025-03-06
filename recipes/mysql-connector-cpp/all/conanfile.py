import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import get, copy, rm, export_conandata_patches, apply_conandata_patches, replace_in_file
from conan.tools.microsoft import is_msvc_static_runtime

required_conan_version = ">=2.0.9"

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
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        copy(self, "conan_project_include.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))
        export_conandata_patches(self)

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
        check_min_cppstd(self, 17)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.24 <4]")
        self.tool_requires("protobuf/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        self._patch_sources()

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_PROJECT_MySQL_CONCPP_INCLUDE"] = os.path.join(self.source_folder, "conan_project_include.cmake")
        tc.cache_variables["BUNDLE_DEPENDENCIES"] = False
        tc.cache_variables["BUILD_STATIC"] = not self.options.shared
        tc.cache_variables["STATIC_MSVCRT"] = is_msvc_static_runtime(self)
        tc.cache_variables["WITH_TESTS"] = False
        tc.cache_variables["CMAKE_TRY_COMPILE_CONFIGURATION"] = str(self.settings.build_type)
        tc.cache_variables["WITH_SSL"] = self.dependencies["openssl"].package_folder.replace("\\", "/")
        tc.cache_variables["CMAKE_PREFIX_PATH"] = self.generators_folder.replace("\\", "/")
        tc.cache_variables["IS64BIT"] = True
        tc.cache_variables["use_full_protobuf"] = not self.dependencies["protobuf"].options.lite
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
        # Disable boostrap(), which is unnecessary and fragile with variables set by Conan
        # https://github.com/mysql/mysql-connector-cpp/blob/9.0.0/CMakeLists.txt#L69-L71
        # https://github.com/mysql/mysql-connector-cpp/blob/9.0.0/cdk/cmake/bootstrap.cmake#L55
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "bootstrap()", "")

    def build(self):
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
            self.cpp_info.libdirs = [os.path.join("lib", "vs14")]
            self.cpp_info.bindirs = ["lib"]
            self.cpp_info.system_libs.extend(["dnsapi", "ws2_32"])
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread", "dl"])
        if self.settings.os == "SunOS":
            self.cpp_info.system_libs.append(["socket", "nsl"])
        if self.settings.os not in ["Windows", "FreeBSD"]:
            self.cpp_info.system_libs.append("resolv")

        if not self.options.shared:
            self.cpp_info.defines = ["MYSQL_STATIC", "STATIC_CONCPP"]
