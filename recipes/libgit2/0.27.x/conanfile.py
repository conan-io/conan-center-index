from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc_static_runtime, is_msvc
from conan.tools.apple import is_apple_os
from conan.tools.files import get, copy, rmdir, replace_in_file
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout

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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        if not is_apple_os(self):
            del self.options.with_iconv

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    @property
    def _need_openssl(self):
        return "openssl" in (self.options.with_https, self.options.with_sha1)

    def requirements(self):
        self.requires("zlib/1.2.13")
        self.requires("http_parser/2.9.4")
        if self.options.with_libssh2:
            self.requires("libssh2/1.10.0")
        if self.settings.os != "Windows":
            self.requires("libcurl/7.87.0")
        if self._need_openssl:
            self.requires("openssl/1.1.1t")

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

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

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

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["THREADSAFE"] = self.options.threadsafe
        tc.variables["USE_SSH"] = self.options.with_libssh2
        tc.variables["USE_ICONV"] = self.options.get_safe("with_iconv", False)
        tc.variables["USE_HTTPS"] = self._cmake_https[str(self.options.with_https)]
        tc.variables["SHA1_BACKEND"] = self._cmake_sha1[str(self.options.with_sha1)]
        tc.variables["BUILD_CLAR"] = False
        tc.variables["BUILD_EXAMPLES"] = False
        if is_msvc(self):
            tc.variables["STATIC_CRT"] = is_msvc_static_runtime(self)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"),
                        "FIND_PKGLIBRARIES(LIBSSH2 libssh2)",
                        "FIND_PACKAGE(Libssh2 REQUIRED)\n"
                        "\tSET(LIBSSH2_FOUND ON)\n"
                        "\tSET(LIBSSH2_INCLUDE_DIRS ${Libssh2_INCLUDE_DIRS})\n"
                        "\tSET(LIBSSH2_LIBRARIES ${Libssh2_LIBRARIES})\n"
                        "\tSET(LIBSSH2_LIBRARY_DIRS ${Libssh2_LIB_DIRS})")

        replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"),
                        "FIND_PKGLIBRARIES(CURL libcurl)",
                        "FIND_PACKAGE(CURL REQUIRED)\n")

    def build(self):
        self._patch_sources()
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
