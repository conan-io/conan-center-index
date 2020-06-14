import os

from conans import CMake, ConanFile, tools


class LibrdkafkaConan(ConanFile):
    name = "librdkafka"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/edenhill/librdkafka"
    description = """This is a Kafka C client package.
    A fully featured, portable librdkafka library."""

    topics = ("kafka", "librdkafka")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "zlib": [True, False],
        "zstd": [True, False],
        "plugins": [True, False],
        "ssl": [True, False],
        "sasl": [True, False],
        "lz4": [True, False],
    }
    default_options = {
        "shared": False,
        "zlib": False,
        "zstd": False,
        "plugins": False,
        "ssl": False,
        "sasl": False,
        "lz4": False,
    }
    generators = "cmake"
    exports_sources = "CMakeLists.txt", "patches/**"
    sources_folder = "sources"
    _cmake = None

    def configure(self):
        if self.options.ssl:
            self.options["openssl"].shared = self.options.shared

    def requirements(self):
        if self.options.zlib:
            self.requires.add("zlib/1.2.11")
        if self.options.zstd:
            self.requires.add("zstd/1.4.4")
        if self.options.ssl:
            self.requires.add("openssl/1.1.1d")
        if self.options.lz4:
            self.requires.add("lz4/1.9.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        downloaded_folder_name = "{}-{}".format(self.name, self.version)
        os.rename(downloaded_folder_name, self.sources_folder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(base_path=self.sources_folder, **patch)

    def _configure_cmake(self):
        if self._cmake is not None:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["WITHOUT_OPTIMIZATION"] = (
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
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("*.h", dst="include", src=self.name)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib*", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["rdkafka", "rdkafka++"]
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.system_libs.extend(["crypt32", "ws2_32"])
        else:
            if self.settings.os == "Linux":
                self.cpp_info.system_libs.extend(["pthread", "m"])
        if not self.options.shared:
            self.cpp_info.defines.append("LIBRDKAFKA_STATICLIB")
