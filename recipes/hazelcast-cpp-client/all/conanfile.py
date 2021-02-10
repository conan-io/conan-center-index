import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

class HazelcastCxx(ConanFile):
    name = "hazelcast-cpp-client"
    description = "C++ client library for Hazelcast in-memory database."
    license = "Apache-2.0"
    topics = ("conan", "hazelcast", "client", "database", "cache")
    homepage = "https://github.com/hazelcast/hazelcast-cpp-client"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": False
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate(self):
        if self.settings.os == "Linux" and self.settings.compiler.libcxx!="libstdc++11":
            raise ConanInvalidConfiguration("Requires settings.compiler.libcxx = libstdc++11")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def requirements(self):
        self.requires("boost/1.75.0")
        if self.options.with_openssl:
            self.requires("openssl/1.1.1i")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["WITH_OPENSSL"] = self.options.with_openssl
        self._cmake.definitions["BUILD_STATIC_LIB"] = not self.options.shared
        self._cmake.definitions["BUILD_SHARED_LIB"] = self.options.shared
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "hazelcastcxx"
        self.cpp_info.filenames["cmake_find_package_multi"] = "hazelcastcxx"
        self.cpp_info.names["cmake_find_package"] = "hazelcastcxx"
        self.cpp_info.names["cmake_find_package_multi"] = "hazelcastcxx"

        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.defines = ["BOOST_THREAD_VERSION=5"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
