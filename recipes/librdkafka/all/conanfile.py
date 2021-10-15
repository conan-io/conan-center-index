import os
from conans import CMake, ConanFile, tools

required_conan_version = ">=1.33.0"


class LibrdkafkaConan(ConanFile):
    name = "librdkafka"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/edenhill/librdkafka"
    description = "Librdkafka is an Apache Kafka C/C++ library designed with message delivery reliability and high performance in mind."

    topics = ("kafka", "librdkafka")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "zlib": [True, False],
        "zstd": [True, False],
        "plugins": [True, False],
        "ssl": [True, False],
        "sasl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "zlib": False,
        "zstd": False,
        "plugins": False,
        "ssl": False,
        "sasl": False,
    }
    generators = "cmake", "cmake_find_package", "pkg_config"
    exports_sources = "CMakeLists.txt", "patches/**"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("lz4/1.9.3")
        if self.options.zlib:
            self.requires("zlib/1.2.11")
        if self.options.zstd:
            self.requires("zstd/1.5.0")
        if self.options.ssl:
            self.requires("openssl/1.1.1l")
        if self.options.sasl and self.settings.os != "Windows":
            self.requires("cyrus-sasl/2.1.27")

    def build_requirements(self):
        if self.options.sasl and self.settings.os != "Windows":
            self.build_requires("pkgconf/1.7.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["WITHOUT_OPTIMIZATION"] = self.settings.build_type == "Debug"
        self._cmake.definitions["ENABLE_DEVEL"] = self.settings.build_type == "Debug"
        self._cmake.definitions["RDKAFKA_BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["RDKAFKA_BUILD_EXAMPLES"] = False
        self._cmake.definitions["RDKAFKA_BUILD_TESTS"] = False
        self._cmake.definitions["WITHOUT_WIN32_CONFIG"] = True
        self._cmake.definitions["WITH_BUNDLED_SSL"] = False
        self._cmake.definitions["WITH_ZLIB"] = self.options.zlib
        self._cmake.definitions["WITH_ZSTD"] = self.options.zstd
        self._cmake.definitions["WITH_PLUGINS"] = self.options.plugins
        self._cmake.definitions["WITH_SSL"] = self.options.ssl
        self._cmake.definitions["WITH_SASL"] = self.options.sasl
        self._cmake.definitions["ENABLE_LZ4_EXT"] = True
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        with tools.run_environment(self):
            cmake = self._configure_cmake()
            cmake.build()

    def package(self):
        self.copy(pattern="LICENSES.txt", src=self._source_subfolder, dst="licenses")
        with tools.run_environment(self):
            cmake = self._configure_cmake()
            cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "RdKafka"
        self.cpp_info.names["cmake_find_package_multi"] = "RdKafka"
        # rdkafka
        self.cpp_info.components["rdkafka"].names["cmake_find_package"] = "rdkafka"
        self.cpp_info.components["rdkafka"].names["cmake_find_package_multi"] = "rdkafka"
        self.cpp_info.components["rdkafka"].names["pkg_config"] = "rdkafka"
        self.cpp_info.components["rdkafka"].libs = ["rdkafka"]
        self.cpp_info.components["rdkafka"].requires = ["lz4::lz4"]
        if self.options.zlib:
            self.cpp_info.components["rdkafka"].requires.append("zlib::zlib")
        if self.options.zstd:
            self.cpp_info.components["rdkafka"].requires.append("zstd::zstd")
        if self.options.ssl:
            self.cpp_info.components["rdkafka"].requires.append("openssl::openssl")
        if self.options.sasl and self.settings.os != "Windows":
            self.cpp_info.components["rdkafka"].requires.append("cyrus-sasl::cyrus-sasl")
        if self.settings.os == "Windows":
            self.cpp_info.components["rdkafka"].system_libs = ["ws2_32", "secur32"]
            if self.options.ssl:
                self.cpp_info.components["rdkafka"].system_libs.append("crypt32")
        elif self.settings.os == "Linux":
            self.cpp_info.components["rdkafka"].system_libs.extend(["pthread", "rt", "dl", "m"])
        if not self.options.shared:
            self.cpp_info.components["rdkafka"].defines.append("LIBRDKAFKA_STATICLIB")
        # rdkafka++
        self.cpp_info.components["rdkafka++"].names["cmake_find_package"] = "rdkafka++"
        self.cpp_info.components["rdkafka++"].names["cmake_find_package_multi"] = "rdkafka++"
        self.cpp_info.components["rdkafka++"].names["pkg_config"] = "rdkafka++"
        self.cpp_info.components["rdkafka++"].libs = ["rdkafka++"]
        self.cpp_info.components["rdkafka++"].requires = ["rdkafka"]
