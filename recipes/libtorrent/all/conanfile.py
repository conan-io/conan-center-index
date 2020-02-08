from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class LibtorrentConan(ConanFile):
    name = "libtorrent"
    description = "libtorrent is a feature complete C++ bittorrent implementation focusing on efficiency and scalability"
    topics = ("conan", "libtorrent", "p2p", "network", "mesh")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://libtorrent.org"
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake"
    license = ("BSD-3-clause", "ZLIB", "BSL-1.0")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_deprecated_functions": [True, False],
        "enable_dht": [True, False],
        "enable_encryption": [True, False],
        "enable_exceptions": [True, False],
        "enable_extensions": [True, False],
        "enable_i2p": [True, False],
        "enable_iconv": [True, False],
        "enable_logging": [True, False],
        "enable_mutable_torrents": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_dht": True,
        "enable_deprecated_functions": True,
        "enable_encryption": True,
        "enable_exceptions": True,
        "enable_extensions": True,
        "enable_i2p": True,
        "enable_iconv": False,
        "enable_logging": True,
        "enable_mutable_torrents": True,
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

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd and self.settings.compiler.cppstd in ("98", "gnu98"):
            raise ConanInvalidConfiguration("libtorrent requires at least c++11")

    def requirements(self):
        self.requires("boost/1.71.0")
        if self.options.enable_encryption:
            self.requires("openssl/1.1.1d")
        if self.options.enable_iconv:
            self.requires("libiconv/1.15")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libtorrent-rasterbar-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["Boost_USE_STATIC_LIBS"] = not self.options["boost"].shared
        self._cmake.definitions["deprecated-functions"] = self.options.enable_deprecated_functions
        self._cmake.definitions["dht"] = self.options.enable_dht
        self._cmake.definitions["encryption"] = self.options.enable_encryption
        self._cmake.definitions["exceptions"] = self.options.enable_exceptions
        self._cmake.definitions["i2p"] = self.options.enable_i2p
        self._cmake.definitions["logging"] = self.options.enable_logging
        self._cmake.definitions["mutable-torrents"] = self.options.enable_mutable_torrents
        self._cmake.definitions["build_tests"] = False
        self._cmake.definitions["build_examples"] = False
        self._cmake.definitions["build_tools"] = False
        self._cmake.definitions["python-bindings"] = False
        self._cmake.definitions["python-bindings"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch_data in self.conan_data["patches"][self.version]:
            tools.patch(**patch_data)

        if self.options.enable_iconv:
            replace = "find_public_dependency(Iconv REQUIRED)"
        else:
            replace = "set(Iconv_FOUND OFF)"
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "find_public_dependency(Iconv)",
                              replace)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libtorrent-rasterbar"
        self.cpp_info.names["cmake_find_package"] = "LibtorrentRasterbar"
        self.cpp_info.names["cmake_find_package_multi"] = "LibtorrentRasterbar"
        self.cpp_info.includedirs = ["include", os.path.join("include", "libtorrent")]
        self.cpp_info.libs = ["torrent-rasterbar"]

        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl", "pthread"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["wsock32", "ws2_32", "iphlpapi", "debug", "dbghelp"]
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks = ["CoreFoundation", "SystemConfiguration"]
