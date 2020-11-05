import os.path
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class CassandraCppDriverConan(ConanFile):
    name = "cassandra-cpp-driver"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://docs.datastax.com/en/developer/cpp-driver/"
    description = "DataStax C/C++ Driver for Apache Cassandra and DataStax Products"
    topics = ("cassandra", "cpp-driver", "database", "conan-recipe")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "install_header_in_subdir": [True, False],
        "use_atomic": [None, "boost", "std"],
        "with_openssl": [True, False],
        "with_zlib": [True, False],
        "with_kerberos": [True, False],
        "use_timerfd": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "install_header_in_subdir": False,
        "use_atomic": None,
        "with_openssl": True,
        "with_zlib": True,
        "with_kerberos": False,
        "use_timerfd": True
    }

    generators = "cmake"
    exports_sources = [
        "CMakeLists.txt",
        "patches/*"
    ]

    _cmake = None

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
            
        self._cmake = CMake(self)
        self._cmake.definitions["VERSION"] = self.version
        self._cmake.definitions["CASS_BUILD_EXAMPLES"] = False
        self._cmake.definitions["CASS_BUILD_INTEGRATION_TESTS"] = False
        self._cmake.definitions["CASS_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["CASS_BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["CASS_BUILD_TESTS"] = False
        self._cmake.definitions["CASS_BUILD_UNIT_TESTS"] = False
        self._cmake.definitions["CASS_DEBUG_CUSTOM_ALLOC"] = False
        self._cmake.definitions["CASS_INSTALL_HEADER_IN_SUBDIR"] = self.options.install_header_in_subdir
        self._cmake.definitions["CASS_INSTALL_PKG_CONFIG"] = False

        if self.options.use_atomic == "boost":
            self._cmake.definitions["CASS_USE_BOOST_ATOMIC"] = True
            self._cmake.definitions["CASS_USE_STD_ATOMIC"] = False

        elif self.options.use_atomic == "std":
            self._cmake.definitions["CASS_USE_BOOST_ATOMIC"] = False
            self._cmake.definitions["CASS_USE_STD_ATOMIC"] = True
        else:
            self._cmake.definitions["CASS_USE_BOOST_ATOMIC"] = False
            self._cmake.definitions["CASS_USE_STD_ATOMIC"] = False

        self._cmake.definitions["CASS_USE_OPENSSL"] = self.options.with_openssl
        self._cmake.definitions["CASS_USE_STATIC_LIBS"] = False
        self._cmake.definitions["CASS_USE_ZLIB"] = self.options.with_zlib
        self._cmake.definitions["CASS_USE_LIBSSH2"] = False

        # FIXME: To use kerberos, its conan package is needed. Uncomment this when kerberos conan package is ready.
        # self._cmake.definitions["CASS_USE_KERBEROS"] = self.options.with_kerberos
        
        if self.settings.os == "Linux":
            self._cmake.definitions["CASS_USE_TIMERFD"] = self.options.use_timerfd

        self._cmake.configure()
        return self._cmake

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.use_timerfd

    def configure(self):
        if self.settings.os == "Macos":
            raise ConanInvalidConfiguration("Macos is unsupported")

        if self.options.use_atomic == "boost":
            # Compilation error on Linux
            if self.settings.os == "Linux":
                raise ConanInvalidConfiguration(
                    "Boost.Atomic is not supported on Linux at the moment")

        if self.options.with_kerberos:
            raise ConanInvalidConfiguration(
                "Kerberos is not supported at the moment")

    def requirements(self):
        self.requires("libuv/1.34.2")
        self.requires("http_parser/2.9.2")
        self.requires("rapidjson/cci.20200410")

        if self.options.with_openssl:
            self.requires("openssl/1.1.1h")

        if self.options.with_zlib:
            self.requires("minizip/1.2.11")
            self.requires("zlib/1.2.11")

        if self.options.use_atomic == "boost":
            self.requires("boost/1.74.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("cpp-driver-{}".format(self.version), self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == "Windows":
            self.cpp_info.libs.extend(["iphlpapi", "psapi", "wsock32",
                "crypt32", "ws2_32", "userenv", "version"])
            if not self.options.shared:
                self.cpp_info.defines = ["CASS_STATIC"]
