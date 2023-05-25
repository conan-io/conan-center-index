from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake
from conan.tools.files import get
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, cross_building, stdcpp_library

class MysqlConnectorCPPRecipe(ConanFile):
    name = "mysql-connector-cpp"
    license = "GPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://dev.mysql.com/doc/connector-cpp/8.0"
    description = "A Conan package for MySQL Connector/C++ with OpenSSL, Boost, and libmysqlclient"
    topics = ("mysql", "connector", "cpp", "openssl", "boost", "libmysqlclient", "jdbc", "static")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    requires = ("boost/1.81.0", "openssl/[>=1.1 <4]", "libmysqlclient/8.0.31")

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

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self.source_folder)

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

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_BUILD_TYPE"] = "Release"
        tc.cache_variables["WITH_JDBC"] = "ON"
        tc.cache_variables["WITHOUT_SERVER"] = "ON"
        if not self.options.shared:
            tc.cache_variables["BUILD_STATIC"] = "ON"
        tc.cache_variables["MYSQL_LIB_DIR"] = self.dependencies["libmysqlclient"].cpp_info.aggregated_components().libdirs[0].replace("\\", "/")
        tc.cache_variables["MYSQL_INCLUDE_DIR"] = self.dependencies["libmysqlclient"].cpp_info.aggregated_components().includedirs[0].replace("\\", "/")
        tc.cache_variables["WITH_SSL"] = self.dependencies["openssl"].package_folder.replace("\\", "/")
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libdirs = ["lib","lib64"]
        self.cpp_info.includedirs = ["include"]
        if not self.options.shared:
            self.cpp_info.libs = ["mysqlcppconn-static", "mysqlcppconn8-static"]
            stdcpplib = stdcpp_library(self)
            if stdcpplib:
                self.cpp_info.system_libs.append(stdcpplib)
            if self.settings.os in ["Linux", "FreeBSD", "Macos"]:
                self.cpp_info.system_libs.extend(["m", "resolv"])
        else:
            self.cpp_info.libs = ["mysqlcppconn", "mysqlcppconn8"]
        self.cpp_info.names["cmake_find_package"] = "mysql-connector-cpp"
        self.cpp_info.names["cmake_find_package_multi"] = "mysql-connector-cpp"
