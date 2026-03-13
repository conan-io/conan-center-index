from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=2.1"


class CpphttplibConan(ConanFile):
    name = "cpp-httplib"
    description = "A C++11 single-file header-only cross platform HTTP/HTTPS library."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/yhirose/cpp-httplib"
    topics = ("http", "https", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_openssl": [True, False],
        "with_mbedtls": [True, False],
        "with_wolfssl": [True, False],
        "with_zlib": [True, False],
        "with_brotli": [True, False],
        "use_macos_keychain_certs": [True, False],
        "with_zstd": [True, False],
    }
    default_options = {
        "with_openssl": False,
        "with_mbedtls": False,
        "with_wolfssl": False,
        "with_zlib": False,
        "with_brotli": False,
        "use_macos_keychain_certs": True,
        "with_zstd": False,
    }
    no_copy_source = True

    def _tls_enabled(self):
        return self.options.with_openssl or self.options.with_mbedtls or self.options.with_wolfssl

    def config_options(self):
        if self.settings.os != "Macos":
            del self.options.use_macos_keychain_certs

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/[>=3 <4]")
        if self.options.with_mbedtls:
            self.requires("mbedtls/3.6.5")
        if self.options.with_wolfssl:
            self.requires("wolfssl/5.7.2")
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_brotli:
            self.requires("brotli/1.1.0")
        if self.options.get_safe("with_zstd"):
            self.requires("zstd/[>=1.5 <1.6]")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 11)

        if self.options.with_mbedtls and Version(self.version) < "0.36.0":
            raise ConanInvalidConfiguration("with_mbedtls option not available, please use version 0.36.0 or newer")

        if self.options.with_wolfssl:
            if Version(self.version) < "0.36.0":
                raise ConanInvalidConfiguration("with_wolfssl option not available, please use version 0.36.0 or newer")
            if not self.dependencies["wolfssl"].options.opensslall:
                raise ConanInvalidConfiguration(f"{self.ref} requires wolfssl/*:opensslall=True.")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "httplib.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include", "httplib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "httplib")
        self.cpp_info.set_property("cmake_target_name", "httplib::httplib")
        self.cpp_info.includedirs.append(os.path.join("include", "httplib"))
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        if self.options.with_openssl:
            self.cpp_info.defines.append("CPPHTTPLIB_OPENSSL_SUPPORT")
        if self.options.with_mbedtls:
            self.cpp_info.defines.append("CPPHTTPLIB_MBEDTLS_SUPPORT")
        if self.options.with_wolfssl:
            self.cpp_info.defines.append("CPPHTTPLIB_WOLFSSL_SUPPORT")
        if self.options.with_zlib:
            self.cpp_info.defines.append("CPPHTTPLIB_ZLIB_SUPPORT")
        if self.options.with_brotli:
            self.cpp_info.defines.append("CPPHTTPLIB_BROTLI_SUPPORT")
        if self.options.get_safe("with_zstd"):
            self.cpp_info.defines.append("CPPHTTPLIB_ZSTD_SUPPORT")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "anl"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["crypt32", "cryptui", "ws2_32"]
        elif self.settings.os == "Macos":
            if self._tls_enabled() and self.options.get_safe("use_macos_keychain_certs"):
                self.cpp_info.frameworks.extend(["CFNetwork", "CoreFoundation", "Security"])
                if Version(self.version) < "0.36.0":
                    self.cpp_info.defines.append("CPPHTTPLIB_USE_CERTS_FROM_MACOSX_KEYCHAIN")

            if not self.options.get_safe("use_macos_keychain_certs") and Version(self.version) >= "0.36.0":
                self.cpp_info.defines.append("CPPHTTPLIB_DISABLE_MACOSX_AUTOMATIC_ROOT_CERTIFICATES")

        self.cpp_info.defines.append("CPPHTTPLIB_USE_NON_BLOCKING_GETADDRINFO")
