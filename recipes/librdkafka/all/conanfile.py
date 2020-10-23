import os

from conans import CMake, ConanFile, tools


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
        "lz4": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "zlib": False,
        "zstd": False,
        "plugins": False,
        "ssl": False,
        "sasl": False,
        "lz4": False,
    }
    generators = "cmake", "cmake_find_package"
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
        if self.options.zlib:
            self.requires("zlib/1.2.11")
        if self.options.zstd:
            self.requires("zstd/1.4.5")
        if self.options.ssl:
            self.requires("openssl/1.1.1g")
        if self.options.sasl and self.settings.os != "Windows":
            self.requires("cyrus-sasl/2.1.27")
        if self.options.lz4:
            self.requires("lz4/1.9.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        downloaded_folder_name = "{}-{}".format(self.name, self.version)
        os.rename(downloaded_folder_name, self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake is not None:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["WITHOUT_OPTIMIZATION"] = (
            self.settings.build_type == "Debug"
        )
        self._cmake.definitions["ENABLE_DEVEL"] = self.settings.build_type == "Debug"
        self._cmake.definitions["ENABLE_REFCNT_DEBUG"] = (
            self.settings.build_type == "Debug"
        )
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
        self._cmake.definitions["ENABLE_LZ4_EXT"] = self.options.lz4
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSES.txt", src=self._source_subfolder, dst="licenses")
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
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.components["rdkafka"].system_libs.extend(["crypt32", "ws2_32"])
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
