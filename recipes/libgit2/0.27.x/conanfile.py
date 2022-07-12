from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.45.0"


class LibGit2Conan(ConanFile):
    name = "libgit2"
    description = (
        "libgit2 is a portable, pure C implementation of the Git core methods "
        "provided as a re-entrant linkable library with a solid API"
    )
    topics = ("libgit2", "git", "scm")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libgit2.org/"
    license = "GPL-2.0-linking-exception"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "threadsafe": [True, False],
        "with_iconv": [True, False],
        "with_libssh2": [True, False],
        "with_https": [False, "openssl", "winhttp", "security"],
        "with_sha1": ["collisiondetection", "commoncrypto", "openssl", "generic", "win32"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "threadsafe": True,
        "with_iconv": False,
        "with_libssh2": True,
        "with_https": "openssl",
        "with_sha1": "collisiondetection",
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        if not tools.is_apple_os(self.settings.os):
            del self.options.with_iconv

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    @property
    def _need_openssl(self):
        return "openssl" in (self.options.with_https, self.options.with_sha1)

    def requirements(self):
        self.requires("zlib/1.2.12")
        self.requires("http_parser/2.9.4")
        if self.options.with_libssh2:
            self.requires("libssh2/1.10.0")
        if self.settings.os != "Windows":
            self.requires("libcurl/7.83.1")
        if self._need_openssl:
            self.requires("openssl/1.1.1o")

    def validate(self):
        if self.options.with_https == "security":
            if not tools.is_apple_os(self.settings.os):
                raise ConanInvalidConfiguration("security is only valid for Apple products")
        elif self.options.with_https == "winhttp":
            if self.settings.os != "Windows":
                raise ConanInvalidConfiguration("winhttp is only valid on Windows")

        if self.options.with_sha1 == "win32":
            if self.settings.os != "Windows":
                raise ConanInvalidConfiguration("win32 is only valid on Windows")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    _cmake_https = {
        "openssl": "OpenSSL",
        "winhttp": "WinHTTP",
        "security": "SecureTransport",
        False: "OFF",
    }

    _cmake_sha1 = {
        "collisiondetection": "CollisionDetection",
        "commoncrypto": "CommonCrypto",
        "openssl": "OpenSSL",
        "generic": "Generic",
        "win32": "Win32",
    }

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["THREADSAFE"] = self.options.threadsafe
        cmake.definitions["USE_SSH"] = self.options.with_libssh2

        cmake.definitions["USE_ICONV"] = self.options.get_safe("with_iconv", False)

        cmake.definitions["USE_HTTPS"] = self._cmake_https[str(self.options.with_https)]
        cmake.definitions["SHA1_BACKEND"] = self._cmake_sha1[str(self.options.with_sha1)]

        cmake.definitions["BUILD_CLAR"] = False
        cmake.definitions["BUILD_EXAMPLES"] = False

        if is_msvc(self):
            cmake.definitions["STATIC_CRT"] = is_msvc_static_runtime(self)

        cmake.configure()
        return cmake

    def _patch_sources(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "CMakeLists.txt"),
                              "FIND_PKGLIBRARIES(LIBSSH2 libssh2)",
                              "FIND_PACKAGE(Libssh2 REQUIRED)\n"
                              "\tSET(LIBSSH2_FOUND ON)\n"
                              "\tSET(LIBSSH2_INCLUDE_DIRS ${Libssh2_INCLUDE_DIRS})\n"
                              "\tSET(LIBSSH2_LIBRARIES ${Libssh2_LIBRARIES})\n"
                              "\tSET(LIBSSH2_LIBRARY_DIRS ${Libssh2_LIB_DIRS})")

        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "CMakeLists.txt"),
                              "FIND_PKGLIBRARIES(CURL libcurl)",
                              "FIND_PACKAGE(CURL REQUIRED)\n")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libgit2")
        self.cpp_info.libs = ["git2"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["winhttp", "rpcrt4", "crypt32"])
        if self.settings.os in ["Linux", "FreeBSD"] and self.options.threadsafe:
            self.cpp_info.system_libs.append("pthread")
