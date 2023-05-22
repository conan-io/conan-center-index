from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, replace_in_file, rm
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.build import check_min_cppstd
import os

required_conan_version = ">=1.53.0"

class CassandraCppDriverConan(ConanFile):
    name = "cassandra-cpp-driver"
    description = "DataStax C/C++ Driver for Apache Cassandra and DataStax Products"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://docs.datastax.com/en/developer/cpp-driver/"
    topics = ("cassandra", "cpp-driver", "database",)
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "install_header_in_subdir": [True, False],
        "use_atomic": [None, "boost", "std"],
        "with_openssl": [True, False],
        "with_zlib": [True, False],
        "with_kerberos": [True, False],
        "use_timerfd": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "install_header_in_subdir": False,
        "use_atomic": None,
        "with_openssl": True,
        "with_zlib": True,
        "with_kerberos": False,
        "use_timerfd": True,
    }
    short_paths = True

    @property
    def _min_cppstd(self):
        return 11

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.use_timerfd

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libuv/1.44.2")
        self.requires("http_parser/2.9.4")
        self.requires("rapidjson/cci.20220822")

        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")

        if self.options.with_zlib:
            self.requires("minizip/1.2.13")
            self.requires("zlib/1.2.13")

        if self.options.use_atomic == "boost":
            self.requires("boost/1.81.0")

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

        if self.options.use_atomic == "boost":
            # Compilation error on Linux
            if self.settings.os == "Linux":
                raise ConanInvalidConfiguration(
                    "Boost.Atomic is not supported on Linux at the moment")

        if self.options.with_kerberos:
            raise ConanInvalidConfiguration(
                "Kerberos is not supported at the moment")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["VERSION"] = self.version
        tc.variables["CASS_BUILD_EXAMPLES"] = False
        tc.variables["CASS_BUILD_INTEGRATION_TESTS"] = False
        tc.variables["CASS_BUILD_SHARED"] = self.options.shared
        tc.variables["CASS_BUILD_STATIC"] = not self.options.shared
        tc.variables["CASS_BUILD_TESTS"] = False
        tc.variables["CASS_BUILD_UNIT_TESTS"] = False
        tc.variables["CASS_DEBUG_CUSTOM_ALLOC"] = False
        tc.variables["CASS_INSTALL_HEADER_IN_SUBDIR"] = self.options.install_header_in_subdir
        tc.variables["CASS_INSTALL_PKG_CONFIG"] = False

        if self.options.use_atomic == "boost":
            tc.variables["CASS_USE_BOOST_ATOMIC"] = True
            tc.variables["CASS_USE_STD_ATOMIC"] = False

        elif self.options.use_atomic == "std":
            tc.variables["CASS_USE_BOOST_ATOMIC"] = False
            tc.variables["CASS_USE_STD_ATOMIC"] = True
        else:
            tc.variables["CASS_USE_BOOST_ATOMIC"] = False
            tc.variables["CASS_USE_STD_ATOMIC"] = False

        tc.variables["CASS_USE_OPENSSL"] = self.options.with_openssl
        tc.variables["CASS_USE_STATIC_LIBS"] = False
        tc.variables["CASS_USE_ZLIB"] = self.options.with_zlib
        tc.variables["CASS_USE_LIBSSH2"] = False

        # FIXME: To use kerberos, its conan package is needed. Uncomment this when kerberos conan package is ready.
        # tc.variables["CASS_USE_KERBEROS"] = self.options.with_kerberos

        if self.settings.os == "Linux":
            tc.variables["CASS_USE_TIMERFD"] = self.options.use_timerfd
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                              "\"${CMAKE_CXX_COMPILER_ID}\" STREQUAL \"Clang\"",
                              "\"${CMAKE_CXX_COMPILER_ID}\" STREQUAL \"Clang\" OR \"${CMAKE_CXX_COMPILER_ID}\" STREQUAL \"AppleClang\"")
        rm(self, "Findlibssh2.cmake", os.path.join(self.source_folder, "cmake"))
        rm(self, "Findlibuv.cmake", os.path.join(self.source_folder, "cmake"))
        rm(self, "FindOpenSSL.cmake", os.path.join(self.source_folder, "cmake"))

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["cassandra" if self.options.shared else "cassandra_static"]

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["iphlpapi", "psapi", "wsock32",
                "crypt32", "ws2_32", "userenv", "version"])
            if not self.options.shared:
                self.cpp_info.defines = ["CASS_STATIC"]
