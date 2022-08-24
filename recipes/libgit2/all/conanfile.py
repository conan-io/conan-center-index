from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
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
        "with_https": [False, "openssl", "mbedtls", "winhttp", "security"],
        "with_sha1": ["collisiondetection", "commoncrypto", "openssl", "mbedtls", "generic", "win32"],
        "with_ntlmclient": [True, False],
        "with_regex": ["builtin", "pcre", "pcre2", "regcomp_l", "regcomp"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "threadsafe": True,
        "with_iconv": False,
        "with_libssh2": True,
        "with_https": "openssl",
        "with_sha1": "collisiondetection",
        "with_ntlmclient": True,
        "with_regex": "builtin",
    }
    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        if not tools.apple.is_apple_os(self):
            del self.options.with_iconv

        if self.settings.os == "Windows":
            del self.options.with_ntlmclient

        if self.settings.os == "Macos":
            self.options.with_regex = "regcomp_l"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def requirements(self):
        self.requires("zlib/1.2.12")
        self.requires("http_parser/2.9.4")
        if self.options.with_libssh2:
            self.requires("libssh2/1.10.0")
        if self._need_openssl:
            self.requires("openssl/1.1.1o")
        if self._need_mbedtls:
            self.requires("mbedtls/3.1.0")
        if self.options.get_safe("with_iconv"):
            self.requires("libiconv/1.16")
        if self.options.with_regex == "pcre":
            self.requires("pcre/8.45")
        elif self.options.with_regex == "pcre2":
            self.requires("pcre2/10.40")

    @property
    def _need_openssl(self):
        return "openssl" in (self.options.with_https, self.options.with_sha1)

    @property
    def _need_mbedtls(self):
        return "mbedtls" in (self.options.with_https, self.options.with_sha1)

    def validate(self):
        if self.options.with_https == "security":
            if not tools.apple.is_apple_os(self):
                raise ConanInvalidConfiguration("security is only valid for Apple products")
        elif self.options.with_https == "winhttp":
            if self.settings.os != "Windows":
                raise ConanInvalidConfiguration("winhttp is only valid on Windows")

        if self.options.with_sha1 == "win32":
            if self.settings.os != "Windows":
                raise ConanInvalidConfiguration("win32 is only valid on Windows")

        if self.options.with_regex == "regcomp" or self.options.with_regex == "regcomp_l":
            if self.settings.compiler == "Visual Studio":
                raise ConanInvalidConfiguration("{} isn't supported by Visual Studio".format(self.options.with_regex))

        if self.settings.os in ["iOS", "tvOS", "watchOS"] and self.options.with_regex == "regcomp_l":
            raise ConanInvalidConfiguration("regcomp_l isn't supported on {}".format(self.settings.os))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    _cmake_https = {
        "openssl": "OpenSSL",
        "winhttp": "WinHTTP",
        "security": "SecureTransport",
        "mbedtls": "mbedTLS",
        False: "OFF",
    }

    _cmake_sha1 = {
        "collisiondetection": "CollisionDetection",
        "commoncrypto": "CommonCrypto",
        "openssl": "OpenSSL",
        "mbedtls": "mbedTLS",
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
        cmake.definitions["USE_SHA1"] = self._cmake_sha1[str(self.options.with_sha1)]

        if tools.scm.Version(self.version) >= "1.4.0":
            cmake.definitions["BUILD_TESTS"] = False
        cmake.definitions["BUILD_CLAR"] = False
        cmake.definitions["BUILD_EXAMPLES"] = False
        cmake.definitions["USE_HTTP_PARSER"] = "system"

        cmake.definitions["REGEX_BACKEND"] = self.options.with_regex

        if is_msvc(self):
            cmake.definitions["STATIC_CRT"] = is_msvc_static_runtime(self)

        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libgit2")
        self.cpp_info.libs = ["git2"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["winhttp", "rpcrt4", "crypt32"])
        if self.settings.os in ["Linux", "FreeBSD"] and self.options.threadsafe:
            self.cpp_info.system_libs.append("pthread")
