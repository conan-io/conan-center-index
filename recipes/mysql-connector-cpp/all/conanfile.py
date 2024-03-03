from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, CMakeDeps, cmake_layout
from conan.tools.files import get, replace_in_file, rm, collect_libs, copy
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc
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
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], "with_jdbc": [True, False]}
    default_options = {"shared": False, "fPIC": True, "with_jdbc": True}

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
        self.tool_requires("protobuf/3.21.12")

    def requirements(self):
        self.requires("zlib/[>=1.2.10 <2]")
        self.requires("lz4/1.9.4")
        self.requires("zstd/1.5.5")
        self.requires("protobuf/3.21.12")
        self.requires("boost/1.83.0")
        self.requires("openssl/[>=1.1.1 <4]")
        self.requires("libmysqlclient/8.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self.source_folder)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 192)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")

        # I dont have a windows computer to test it
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support windows for now")

        # Sice 8.0.17 this doesn't support shared library on MacOS.
        # https://github.com/mysql/mysql-server/blob/mysql-8.0.17/cmake/libutils.cmake#L333-L335
        if self.settings.compiler == "apple-clang" and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support shared library on apple-clang")

        # mysql < 8.0.29 uses `requires` in source code. It is the reserved keyword in C++20.
        # https://github.com/mysql/mysql-server/blob/mysql-8.0.0/include/mysql/components/services/dynamic_loader.h#L270
        if self.settings.compiler.get_safe("cppstd") == "20" and Version(self.version) < "8.0.29":
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support C++20")

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
        tc.presets_build_environment = env.environment()
        tc.variables["WITH_JDBC"] = True
        tc.variables["WITHOUT_SERVER"] = True
        # INFO: mysql-connector-cpp caches all option values. Need to use cache_variables
        tc.cache_variables["BUILD_STATIC"] = not self.options.shared
        # INFO: mysql-connector-cpp doesn't use find package for cmake. Need to pass manually folder paths
        tc.variables["MYSQL_LIB_DIR"] = self._lib_folder_dep("libmysqlclient")
        tc.variables["MYSQL_INCLUDE_DIR"] = self._include_folder_dep("libmysqlclient")
        tc.variables["Boost_INCLUDE_DIRS"] = self._include_folder_dep("boost")
        tc.variables["Boost_LIB_DIRS"] = self._lib_folder_dep("boost")
        # INFO: Some dependencies can be found in mysql-connector-cpp source folder. Need to set to use Conan package
        tc.cache_variables["WITH_SSL"] = self._package_folder_dep("openssl")
        tc.cache_variables["WITH_BOOST"] = self._package_folder_dep("boost")
        tc.cache_variables["WITH_ZLIB"] = self._package_folder_dep("zlib")
        tc.cache_variables["WITH_LZ4"] = self._package_folder_dep("lz4")
        tc.cache_variables["WITH_ZSTD"] = self._package_folder_dep("zstd")
        tc.cache_variables["WITH_PROTOBUF"] = self._package_folder_dep("protobuf")
        if self.options.with_jdbc:
            tc.variables["JDBC_ENABLED"] = True
        tc.generate()

    def _patch_sources(self):
       # INFO: Disable internal bootstrap to use Conan CMakeToolchain instead
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "bootstrap()", "")
        # INFO: Manage fPIC from recipe options
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "enable_pic()", "")
        replace_in_file(self, os.path.join(self.source_folder, "cdk", "CMakeLists.txt"), "enable_pic()", "")
        protobuf = "protobufd" if self.dependencies["protobuf"].settings.build_type == "Debug" else "protobuf"
        # INFO: Disable protobuf-lite to use Conan protobuf targets instead
        replace_in_file(self, os.path.join(self.source_folder, "cdk", "cmake", "DepFindProtobuf.cmake"), "LIBRARY protobuf-lite pb_libprotobuf-lite", "")
        # INFO: Fix protobuf library name according to the build type
        replace_in_file(self, os.path.join(self.source_folder, "cdk", "cmake", "DepFindProtobuf.cmake"), "LIBRARY protobuf", f"LIBRARY {protobuf}")
        # INFO: Disable protobuf-lite to use Conan protobuf targets instead
        replace_in_file(self, os.path.join(self.source_folder, "cdk", "protocol", "mysqlx", "CMakeLists.txt"), "ext::protobuf-lite", f"ext::{protobuf}")
        # INFO: Disable protobuf-lite to use Conan protobuf targets instead
        replace_in_file(self, os.path.join(self.source_folder, "cdk", "core", "CMakeLists.txt"), "ext::protobuf-lite", f"ext::{protobuf}")
        if self.settings.os == "Windows":
            # INFO: On Windows, libraries names change
            zlib = "zdll" if self.dependencies["zlib"].options.shared else "zlib"
            zstd = "zstd" if self.dependencies["zstd"].options.shared else "zstd_static"
            replace_in_file(self, os.path.join(self.source_folder, "cdk", "cmake", "DepFindCompression.cmake"), "add_ext(zlib zlib.h z ext_zlib)", f"add_ext(zlib zlib.h {zlib} ext_zlib)")
            replace_in_file(self, os.path.join(self.source_folder, "cdk", "protocol", "mysqlx", "CMakeLists.txt"), "ext::z ext::lz4 ext::zstd", f"ext::{zlib} ext::lz4 ext::{zstd}")
            replace_in_file(self, os.path.join(self.source_folder, "cdk", "cmake", "DepFindCompression.cmake"), "add_ext(zstd zstd.h zstd ext_zstd)", f"add_ext(zstd zstd.h {zstd} ext_zstd)")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.parallel = True
        cmake.verbose = True
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rm(self, "INFO_SRC", self.package_folder)
        rm(self, "INFO_BIN", self.package_folder)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libmysqlcppconn")
        self.cpp_info.includedirs.append(os.path.join("include", "mysql"))
        self.cpp_info.includedirs.append(os.path.join("include", "mysqlx"))
        self.cpp_info.libdirs = ["lib64/debug","lib/debug"] if self.settings.build_type == "Debug" else ["lib64", "lib"]
        self.cpp_info.libs = collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD", "Macos"]:
            self.cpp_info.system_libs = ["m", "resolv"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
