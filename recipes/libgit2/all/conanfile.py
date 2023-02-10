from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc_static_runtime, is_msvc
from conan.tools.apple import is_apple_os
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
import os

required_conan_version = ">=1.53.0"

class LibGit2Conan(ConanFile):
    name = "libgit2"
    description = (
        "libgit2 is a portable, pure C implementation of the Git core methods "
        "provided as a re-entrant linkable library with a solid API"
    )
    license = "GPL-2.0-linking-exception"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libgit2.org/"
    topics = ("libgit2", "git", "scm")
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

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        if not is_apple_os(self):
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

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/1.2.13")
        self.requires("http_parser/2.9.4")
        if self.options.with_libssh2:
            self.requires("libssh2/1.10.0")
        if self._need_openssl:
            self.requires("openssl/1.1.1s")
        if self._need_mbedtls:
            self.requires("mbedtls/3.2.1")
        if self.options.get_safe("with_iconv"):
            self.requires("libiconv/1.17")
        if self.options.with_regex == "pcre":
            self.requires("pcre/8.45")
        elif self.options.with_regex == "pcre2":
            self.requires("pcre2/10.42")

    @property
    def _need_openssl(self):
        return "openssl" in (self.options.with_https, self.options.with_sha1)

    @property
    def _need_mbedtls(self):
        return "mbedtls" in (self.options.with_https, self.options.with_sha1)

    def validate(self):
        if self.options.with_https == "security":
            if not is_apple_os(self.settings.os):
                raise ConanInvalidConfiguration("security is only valid for Apple products")
        elif self.options.with_https == "winhttp":
            if self.settings.os != "Windows":
                raise ConanInvalidConfiguration("winhttp is only valid on Windows")

        if self.options.with_sha1 == "win32":
            if self.settings.os != "Windows":
                raise ConanInvalidConfiguration("win32 is only valid on Windows")

        if self.options.with_regex == "regcomp" or self.options.with_regex == "regcomp_l":
            if is_msvc(self):
                raise ConanInvalidConfiguration("{} isn't supported by Visual Studio".format(self.options.with_regex))

        if is_apple_os(self) and self.options.with_regex == "regcomp_l":
            raise ConanInvalidConfiguration("regcomp_l isn't supported on {}".format(self.settings.os))

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

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

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["THREADSAFE"] = self.options.threadsafe
        tc.variables["USE_SSH"] = self.options.with_libssh2

        tc.variables["USE_ICONV"] = self.options.get_safe("with_iconv", False)

        tc.variables["USE_HTTPS"] = self._cmake_https[str(self.options.with_https)]
        tc.variables["USE_SHA1"] = self._cmake_sha1[str(self.options.with_sha1)]

        if Version(self.version) >= "1.4.0":
            tc.variables["BUILD_TESTS"] = False
        tc.variables["BUILD_CLAR"] = False
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["USE_HTTP_PARSER"] = "system"

        tc.variables["REGEX_BACKEND"] = self.options.with_regex

        if is_msvc(self):
            tc.variables["STATIC_CRT"] = is_msvc_static_runtime(self)
        tc.generate()

        dpes = CMakeDeps(self)
        dpes.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libgit2")
        self.cpp_info.libs = ["git2"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["winhttp", "rpcrt4", "crypt32"])
        if self.settings.os in ["Linux", "FreeBSD"] and self.options.threadsafe:
            self.cpp_info.system_libs.append("pthread")
