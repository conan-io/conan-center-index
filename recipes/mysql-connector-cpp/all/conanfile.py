from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, CMakeDeps, cmake_layout
from conan.tools.files import get, replace_in_file, rm
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
from conan.tools.build import check_min_cppstd
from conan.tools.env import VirtualBuildEnv
import os


requird_conan_version = ">=1.54.0"


class MysqlConnectorCPPRecipe(ConanFile):
    name = "mysql-connector-cpp"
    license = "GPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://dev.mysql.com/doc/connector-cpp/8.1/en/"
    description = "A MySQL database connector for C++ applications that connect to MySQL servers"
    topics = ("mysql", "connector", "libmysqlclient", "jdbc")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    @property
    def _min_cppstd(self):
        return "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "9" if Version(self.version) >= "8.0.27" else "5.3",
            "clang": "6",
        }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("protobuf/<host_version>")

    def requirements(self):
        self.requires("protobuf/3.21.12")
        self.requires("rapidjson/cci.20220822")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("lz4/1.9.4")
        self.requires("zstd/1.5.5")
        self.requires("openssl/[>=1.1.1 <4]")
        self.requires("libmysqlclient/8.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self.source_folder)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def _package_folder_dep(self, dep):
        return self.dependencies[dep].package_folder.replace("\\", "/")

    def _include_folder_dep(self, dep):
        return self.dependencies[dep].cpp_info.includedirs[0].replace("\\", "/")

    def _lib_folder_dep(self, dep):
        return self.dependencies[dep].cpp_info.libdirs[0].replace("\\", "/")

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate(scope="build")
        tc = CMakeDeps(self)
        tc.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["WITH_JDBC"] = True
        tc.cache_variables["WITH_TESTS"] = False
        tc.cache_variables["WITH_DOC"] = False
        tc.cache_variables["WITH_HEADER_CHECKS"] = False
        # INFO: mysql-connector-cpp caches all option values. Need to use cache_variables
        tc.cache_variables["BUILD_STATIC"] = not self.options.shared
        tc.cache_variables["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        tc.cache_variables["CMAKE_BUILD_TYPE"] = self.settings.build_type
        # INFO: mysql-connector-cpp doesn't use find package for cmake. Need to pass manually folder paths
        tc.cache_variables["MYSQL_LIB_DIR"] = self._lib_folder_dep("libmysqlclient")
        tc.cache_variables["MYSQL_INCLUDE_DIR"] = self._include_folder_dep("libmysqlclient")
        # INFO: Some dependencies can be found in mysql-connector-cpp source folder. Need to set to use Conan package
        tc.cache_variables["WITH_SSL"] = self._package_folder_dep("openssl")
        tc.cache_variables["WITH_MYSQL"] = self._package_folder_dep("libmysqlclient")
        tc.cache_variables["WITH_ZLIB"] = self._package_folder_dep("zlib")
        tc.cache_variables["WITH_LZ4"] = self._package_folder_dep("lz4")
        tc.cache_variables["WITH_ZSTD"] = self._package_folder_dep("zstd")
        tc.cache_variables["WITH_PROTOBUF"] = self._package_folder_dep("protobuf")
        tc.generate()

    def _patch_sources(self):
        # INFO: Disable internal bootstrap to use Conan CMakeToolchain instead
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "bootstrap()", "")
        # INFO: Manage fPIC from recipe options
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "enable_pic()", "")
        replace_in_file(self, os.path.join(self.source_folder, "cdk", "CMakeLists.txt"), "enable_pic()", "")
        # INFO: Disable protobuf-lite to use Conan protobuf targets instead
        replace_in_file(self, os.path.join(self.source_folder, "cdk", "cmake", "DepFindProtobuf.cmake"), "LIBRARY protobuf-lite pb_libprotobuf-lite", "")
        # INFO: Disable protobuf-lite to use Conan protobuf targets instead
        replace_in_file(self, os.path.join(self.source_folder, "cdk", "protocol", "mysqlx", "CMakeLists.txt"), "ext::protobuf-lite", "ext::protobuf")
        # INFO: Disable protobuf-lite to use Conan protobuf targets instead
        replace_in_file(self, os.path.join(self.source_folder, "cdk", "core", "CMakeLists.txt"), "ext::protobuf-lite", "ext::protobuf")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        rm(self, "INFO_SRC", self.package_folder)
        rm(self, "INFO_BIN", self.package_folder)

    def package_info(self):
        suffix = "" if self.options.shared else "-static"
        self.cpp_info.libs = [f"mysqlcppconn8{suffix}", f"mysqlcppconn{suffix}"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "resolv"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
