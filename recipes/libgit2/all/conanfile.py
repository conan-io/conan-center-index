from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
import os


class LibGit2Conan(ConanFile):
    name = "libgit2"
    description = "libgit2 is a portable, pure C implementation of the Git core methods provided as a re-entrant linkable library with a solid API"
    topics = ("conan", "libgit2", "git", "scm", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libgit2.org/"
    license = ("GPL-2.0-linking-exception",)
    exports_sources = "CMakeLists.txt",
    generators = "cmake", "cmake_find_package",
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "threadsafe": [True, False],
        "with_iconv": [True, False],
        "with_libssh2": [True, False],
        "with_https": [False, "openssl", "mbedtls", "winhttp", "security"],
        "with_sha1": ["collisiondetection", "commoncrypto", "openssl", "mbedtls", "generic", "win32"],
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
    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows" or self.options.shared:
            del self.options.fPIC

        if not tools.is_apple_os(self.settings.os):
            del self.options.with_iconv

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

        if self.options.with_https == "security":
            if not tools.is_apple_os(self.settings.os):
                raise ConanInvalidConfiguration("security is only valid for Apple products")
        elif self.options.with_https == "winhttp":
            if self.settings.os != "Windows":
                raise ConanInvalidConfiguration("winhttp is only valid on Windows")

        if self.options.with_sha1 == "win32":
            if self.settings.os != "Windows":
                raise ConanInvalidConfiguration("win32 is only valid on Windows")

    @property
    def _need_openssl(self):
        return "openssl" in (self.options.with_https, self.options.with_sha1)

    @property
    def _need_mbedtls(self):
        return "mbedtls" in (self.options.with_https, self.options.with_sha1)

    def requirements(self):
        self.requires("zlib/1.2.11")
        self.requires("http_parser/2.9.4")
        if self.options.with_libssh2:
            self.requires("libssh2/1.9.0")
        if self._need_openssl:
            self.requires("openssl/1.1.1g")
        if self._need_mbedtls:
            self.requires("mbedtls/2.16.3-gpl")
        if tools.is_apple_os(self.settings.os) and self.options.with_iconv:
            self.requires("libiconv/1.16")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "{}-{}".format(self.name, self.version)
        os.rename(extracted_dir, self._source_subfolder)

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

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["THREADSAFE"] = self.options.threadsafe
        cmake.definitions["USE_SSH"] = self.options.with_libssh2

        if tools.is_apple_os(self.settings.os):
            cmake.definitions["USE_ICONV"] = self.options.with_iconv
        else:
            cmake.definitions["USE_ICONV"] = False

        cmake.definitions["USE_HTTPS"] = self._cmake_https[str(self.options.with_https)]
        cmake.definitions["SHA1_BACKEND"] = self._cmake_sha1[str(self.options.with_sha1)]

        cmake.definitions["BUILD_CLAR"] = False
        cmake.definitions["BUILD_EXAMPLES"] = False

        if self.settings.compiler == "Visual Studio":
            cmake.definitions["STATIC_CRT"] = "MT" in str(self.settings.compiler.runtime)

        cmake.configure()

        return cmake

    def _patch_sources(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "CMakeLists.txt"),
                              "FIND_PKGLIBRARIES(LIBSSH2 libssh2)",
                              "FIND_PACKAGE(libssh2 REQUIRED)\n"
                              "\tSET(LIBSSH2_FOUND ON)\n"
                              "\tSET(LIBSSH2_INCLUDE_DIRS ${libssh2_INCLUDE_DIRS})\n"
                              "\tSET(LIBSSH2_LIBRARIES ${libssh2_LIBRARIES})\n"
                              "\tSET(LIBSSH2_LIBRARY_DIRS ${libssh2_LIB_DIRS})")
        tools.save("FindOpenSSL.cmake",
                   "set(OPENSSL_FOUND ${OpenSSL_FOUND})\n"
                   "set(OPENSSL_INCLUDE_DIR ${OpenSSL_INCLUDE_DIRS})\n"
                   "set(OPENSSL_LIBRARIES ${OpenSSL_LIBRARIES})\n",
                   append=True)

    def build(self):
        self._patch_sources()

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", src=os.path.join(self.source_folder, self._source_subfolder), dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["git2"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["winhttp", "rpcrt4", "crypt32"])
        if self.settings.os == "Linux" and self.options.threadsafe:
            self.cpp_info.system_libs.append("pthread")
