from conan.tools.microsoft import msvc_runtime_flag
from from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class LibtorrentConan(ConanFile):
    name = "libtorrent"
    description = (
        "libtorrent is a feature complete C++ bittorrent implementation "
        "focusing on efficiency and scalability"
    )
    topics = ("libtorrent", "p2p", "network", "mesh")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://libtorrent.org"
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

    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def _check_compiler_supports_cxx14(self):
        min_compiler_version = {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "5",
            "apple-clang": "5",
        }.get(str(self.settings.compiler))
        if min_compiler_version is None:
            self.output.warn("Unknown compiler. Assuming it is supporting c++14")
        if tools.Version(self.settings.compiler.version) < min_compiler_version:
            raise ConanInvalidConfiguration("This compiler (version) does not support c++ 14.")
        return True, None

    def validate(self):
        if tools.Version(self.version) < "2.0":
            if self.settings.compiler.get_safe("cppstd"):
                tools.check_min_cppstd(self, 11)
        else:
            self._check_compiler_supports_cxx14()
            if self.settings.compiler.get_safe("cppstd"):
                tools.check_min_cppstd(self, 14)

    def requirements(self):
        if tools.Version(self.version) < "2.0.0":
            self.requires("boost/1.79.0")
        else:
            self.requires("boost/1.76.0")
        if self.options.enable_encryption:
            self.requires("openssl/1.1.1q")
        if self.options.enable_iconv:
            self.requires("libiconv/1.17")

    def _validate_dependency_graph(self):
        if tools.Version(self.deps_cpp_info["boost"].version) < "1.69.0" and \
           (self.options["boost"].header_only or self.options["boost"].without_system):
            raise ConanInvalidConfiguration("libtorrent requires boost with system, which is non-header only in boost < 1.69.0")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

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
        if self._is_msvc:
            self._cmake.definitions["static_runtime"] = "MT" in msvc_runtime_flag(self)
        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch_data in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch_data)

        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "CMakeLists.txt"), "/W4", "")
        if tools.Version(self.version) < "2.0":
            if self.options.enable_iconv:
                replace = "find_public_dependency(Iconv REQUIRED)"
            else:
                replace = "set(Iconv_FOUND OFF)"
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "CMakeLists.txt"),
                                  "find_public_dependency(Iconv)",
                                  replace)
            if self.settings.compiler == "clang" and self.settings.compiler.libcxx == "libstdc++":
                # https://github.com/arvidn/libtorrent/issues/3557
                tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "include", "libtorrent", "file_storage.hpp"),
                                      "file_entry& operator=(file_entry&&) & noexcept = default;",
                                      "file_entry& operator=(file_entry&&) & = default;")

    def build(self):
        self._validate_dependency_graph()
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "LibtorrentRasterbar")
        self.cpp_info.set_property("cmake_target_name", "LibtorrentRasterbar::torrent-rasterbar")
        self.cpp_info.set_property("pkg_config_name", "libtorrent-rasterbar")

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["libtorrent-rasterbar"].includedirs = ["include", os.path.join("include", "libtorrent")]
        self.cpp_info.components["libtorrent-rasterbar"].libs = ["torrent-rasterbar"]

        self.cpp_info.components["libtorrent-rasterbar"].requires = ["boost::boost"]
        if self.options.enable_encryption:
            self.cpp_info.components["libtorrent-rasterbar"].requires.append("openssl::openssl")
        if self.options.enable_iconv:
            self.cpp_info.components["libtorrent-rasterbar"].requires.append("libiconv::libiconv")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libtorrent-rasterbar"].system_libs = ["dl", "pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["libtorrent-rasterbar"].system_libs = ["wsock32", "ws2_32", "iphlpapi", "dbghelp"]
        elif self.settings.os == "Macos":
            self.cpp_info.components["libtorrent-rasterbar"].frameworks = ["CoreFoundation", "SystemConfiguration"]

        if self.options.shared:
            self.cpp_info.components["libtorrent-rasterbar"].defines.append("TORRENT_LINKING_SHARED")
        if self.options.enable_encryption:
            self.cpp_info.components["libtorrent-rasterbar"].defines.extend(["TORRENT_USE_OPENSSL", "TORRENT_USE_LIBCRYPTO"])
        else:
            self.cpp_info.components["libtorrent-rasterbar"].defines.append("TORRENT_DISABLE_ENCRYPTION")
        if self.options.enable_iconv:
            self.cpp_info.components["libtorrent-rasterbar"].defines.append("TORRENT_USE_ICONV")
        if not self.options.enable_dht:
            self.cpp_info.components["libtorrent-rasterbar"].defines.append("TORRENT_DISABLE_DHT")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "LibtorrentRasterbar"
        self.cpp_info.names["cmake_find_package_multi"] = "LibtorrentRasterbar"
        self.cpp_info.components["libtorrent-rasterbar"].names["cmake_find_package"] = "torrent-rasterbar"
        self.cpp_info.components["libtorrent-rasterbar"].names["cmake_find_package_multi"] = "torrent-rasterbar"
        self.cpp_info.components["libtorrent-rasterbar"].set_property("cmake_target_name", "LibtorrentRasterbar::torrent-rasterbar")
        self.cpp_info.components["libtorrent-rasterbar"].set_property("pkg_config_name", "libtorrent-rasterbar")
