import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class HazelcastCxx(ConanFile):
    name = "hazelcastcxx"
    description = "Hazelcast is C++ API for in memory database."
    license = "Apache 2.0"
    topics = ("conan", "hazelcast", "client", "database", "cache")
    homepage = "https://github.com/hazelcast/hazelcast-cpp-client"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "static": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False]
    }
    default_options = {
        "shared": False,
        "static": True,
        "fPIC": True,
        "with_openssl": False
    }

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

    def validate(self):
        if self.settings.os == "Linux" and self.settings.compiler.libcxx!="libstdc++11":
            raise ConanInvalidConfiguration("Requires settings.compiler.libcxx = libstdc++11")

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def requirements(self):
        self.requires("boost/[>1.71.0]")
        if self.options.with_openssl:
            self.requires("openssl")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("hazelcast-cpp-client-" + self.version, self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _bool_to_cmake_option(self, value):
        return "ON" if value else "OFF"

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.verbose = True
        self._cmake.definitions["WITH_OPENSSL"] = self._bool_to_cmake_option(self.options.with_openssl)
        self._cmake.definitions["BUILD_STATIC_LIB"] = self._bool_to_cmake_option(self.options.static)
        self._cmake.definitions["BUILD_SHARED_LIB"] = self._bool_to_cmake_option(self.options.shared)
        self._cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        if self.options.with_openssl:
            self.cpp_info.names["cmake_find_package"] = "hazelcastcxx_ssl"
            self.cpp_info.names["cmake_find_package_multi"] = "hazelcastcxx_ssl"
        else:
            self.cpp_info.names["cmake_find_package"] = "hazelcastcxx"
            self.cpp_info.names["cmake_find_package_multi"] = "hazelcastcxx"

        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.defines = ["BOOST_THREAD_VERSION=5"]
