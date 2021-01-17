from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class RedisPlusPlusConan(ConanFile):
    name = "redis-plus-plus"
    homepage = "https://github.com/sewenew/redis-plus-plus"
    description = "Redis client written in C++"
    topics = ("conan", "database", "redis", "client", "tls")
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], "with_tls": [True, False]}
    default_options = {"shared": False, "fPIC": True, "with_tls": False}

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

    def validate(self):
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            raise ConanInvalidConfiguration("redis-plus-plus does not support begin compiled as shared on Visual Studio.")
        if self.options.with_tls != self.options["hiredis"].with_ssl:
            raise ConanInvalidConfiguration("with_tls must match hiredis.with_ssl option")

    def requirements(self):
        self.requires("hiredis/1.0.0")
        if self.options.with_tls:
            self.requires("openssl/1.1.1i")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["REDIS_PLUS_PLUS_USE_TLS"] = self.options.with_tls
            self._cmake.definitions["REDIS_PLUS_PLUS_BUILD_TEST"] = False
            self._cmake.definitions["REDIS_PLUS_PLUS_BUILD_STATIC"] = not self.options.shared
            self._cmake.definitions["REDIS_PLUS_PLUS_BUILD_SHARED"] = self.options.shared
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
