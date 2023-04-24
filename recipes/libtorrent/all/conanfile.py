from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, replace_in_file
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class LibtorrentConan(ConanFile):
    name = "libtorrent"
    description = (
        "libtorrent is a feature complete C++ bittorrent implementation "
        "focusing on efficiency and scalability"
    )
    topics = ("p2p", "network", "mesh")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://libtorrent.org"
    license = ("BSD-3-clause", "ZLIB", "BSL-1.0")

    package_type = "library"
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

    @property
    def _min_cppstd(self):
        return "11" if Version(self.version) < "2.0.0" else "14"

    @property
    def _compilers_minimum_version(self):
        return {
            "14": {
                "Visual Studio": "15",
                "msvc": "191",
                "gcc": "5" if Version(self.version) < "2.0.8" else "6",
                "clang": "5",
                "apple-clang": "5",
            },
        }.get(self._min_cppstd, {})

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # libtorrent 2.0.x [x<=6] have issue for recent boost https://github.com/arvidn/libtorrent/discussions/6757
        if Version(self.version) < "2.0.0" or Version(self.version) >= "2.0.7":
            self.requires("boost/1.81.0", transitive_headers=True)
        else:
            self.requires("boost/1.76.0", transitive_headers=True)
        if self.options.enable_encryption:
            self.requires("openssl/[>=1.1 <4]", transitive_headers=True, transitive_libs=True)
        if self.options.enable_iconv:
            self.requires("libiconv/1.17")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if Version(self.dependencies["boost"].ref.version) < "1.69.0" and \
           (self.dependencies["boost"].options.header_only or self.dependencies["boost"].options.without_system):
            raise ConanInvalidConfiguration(f"{self.ref} requires boost with system, which is non-header only in boost < 1.69.0")

    def _cmake_new_enough(self, required_version):
        try:
            import re
            from io import StringIO
            output = StringIO()
            self.run("cmake --version", output)
            m = re.search(r'cmake version (\d+\.\d+\.\d+)', output.getvalue())
            return Version(m.group(1)) >= required_version
        except:
            return False

    def build_requirements(self):
        if Version(self.version) >= "2.0.4" and not self._cmake_new_enough("3.16.0"):
            self.tool_requires("cmake/[^3.16]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = CMakeToolchain(self)
        tc.variables["Boost_USE_STATIC_LIBS"] = not self.dependencies["boost"].options.get_safe("shared", False)
        tc.variables["deprecated-functions"] = self.options.enable_deprecated_functions
        tc.variables["dht"] = self.options.enable_dht
        tc.variables["encryption"] = self.options.enable_encryption
        tc.variables["exceptions"] = self.options.enable_exceptions
        tc.variables["i2p"] = self.options.enable_i2p
        tc.variables["logging"] = self.options.enable_logging
        tc.variables["mutable-torrents"] = self.options.enable_mutable_torrents
        tc.variables["build_tests"] = False
        tc.variables["build_examples"] = False
        tc.variables["build_tools"] = False
        tc.variables["python-bindings"] = False
        tc.variables["python-bindings"] = False
        if is_msvc(self):
            tc.variables["static_runtime"] = is_msvc_static_runtime(self)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "/W4", "")
        if Version(self.version) < "2.0":
            if self.options.enable_iconv:
                replace = "find_public_dependency(Iconv REQUIRED)"
            else:
                replace = "set(Iconv_FOUND OFF)"
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                                  "find_public_dependency(Iconv)",
                                  replace)
            if self.settings.compiler == "clang" and self.settings.compiler.libcxx == "libstdc++":
                # https://github.com/arvidn/libtorrent/issues/3557
                replace_in_file(self, os.path.join(self.source_folder, "include", "libtorrent", "file_storage.hpp"),
                                      "file_entry& operator=(file_entry&&) & noexcept = default;",
                                      "file_entry& operator=(file_entry&&) & = default;")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "LibtorrentRasterbar")
        self.cpp_info.set_property("cmake_target_name", "LibtorrentRasterbar::torrent-rasterbar")
        self.cpp_info.set_property("pkg_config_name", "libtorrent-rasterbar")

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["libtorrent-rasterbar"].includedirs = ["include", os.path.join("include", "libtorrent")]
        self.cpp_info.components["libtorrent-rasterbar"].libs = ["torrent-rasterbar"]

        self.cpp_info.components["libtorrent-rasterbar"].requires = ["boost::headers", "boost::system"]
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
