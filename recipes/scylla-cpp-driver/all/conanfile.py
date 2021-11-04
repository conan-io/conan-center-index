import os
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.33.0"


class ScyllaCppDriverConan(ConanFile):
    name = "scylla-cpp-driver"
    homepage = "https://github.com/scylladb/cpp-driver"
    description = "A modern, feature-rich and shard-aware C/C++ client library for ScyllaDB."
    topics = ("conan", "scylla", "scylladb", "driver", "database", "cassandra")
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "boost_atomic": [True, False],
        "kerberos": [True, False],
        "openssl": [True, False],
        "zlib": [True, False],
        "build_static_lib": [True, False],
        "build_shared_lib": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "boost_atomic": False,
        "kerberos": False,
        "openssl": True,
        "zlib": True,
        "build_static_lib": False,
        "build_shared_lib": True,
    }
    short_paths = True

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CASS_BUILD_EXAMPLES"] = False
        self._cmake.definitions["CASS_BUILD_INTEGRATION_TESTS"] = False
        self._cmake.definitions["CASS_BUILD_TESTS"] = False
        self._cmake.definitions["CASS_BUILD_SHARED"] = self.options.build_shared_lib
        self._cmake.definitions["CASS_BUILD_STATIC"] = self.options.build_static_lib
        self._cmake.definitions["CASS_BUILD_UNIT_TESTS"] = False
        self._cmake.definitions["CASS_DEBUG_CUSTOM_ALLOC"] = False
        self._cmake.definitions["CASS_USE_BOOST_ATOMIC"] = self.options.boost_atomic
        self._cmake.definitions["CASS_USE_KERBEROS"] = self.options.kerberos
        self._cmake.definitions["CASS_USE_LIBSSH2"] = False
        self._cmake.definitions["CASS_USE_OPENSSL"] = self.options.openssl
        self._cmake.definitions["CASS_USE_STD_ATOMIC"] = not self.options.boost_atomic
        self._cmake.definitions["CASS_USE_ZLIB"] = self.options.zlib

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("License.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.names["cmake_find_package"] = "ScyllaCppDriver"
        self.cpp_info.names["cmake_find_package_multi"] = "ScyllaCppDriver"
