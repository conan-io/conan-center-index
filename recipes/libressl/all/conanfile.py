from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rm, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import glob
import os

required_conan_version = ">=1.53.0"


class LibreSSLConan(ConanFile):
    name = "libressl"
    topics = ("SSL", "TLS", "openssl")
    description = (
        "LibreSSL is a version of the TLS/crypto stack forked from OpenSSL in "
        "2014, with goals of modernizing the codebase, improving security, and "
        "applying best practice development processes."
    )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.libressl.org/"
    license = ("OpenSSL", "BSD", "ISC")

    provides = "openssl"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.options.shared and is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Static runtime linked into shared LibreSSL not supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LIBRESSL_SKIP_INSTALL"] = False
        tc.variables["LIBRESSL_APPS"] = False # Warning: if enabled, do not use cmake installation, to avoid installing files in OPENSSLDIR
        tc.variables["LIBRESSL_TESTS"] = False
        tc.variables["ENABLE_ASM"] = True
        tc.variables["ENABLE_EXTRATESTS"] = False
        tc.variables["ENABLE_NC"] = False
        tc.variables["OPENSSLDIR"] = "res"
        if is_msvc(self):
            tc.preprocessor_definitions["_CRT_SUPPRESS_RESTRICT"] = 1
        tc.generate()

    def _patch_sources(self):
        if Version(self.version) >= "3.1.1":
            replace_in_file(
                self, os.path.join(self.source_folder, "CMakeLists.txt"),
                "cmake_minimum_required (VERSION 3.16.4)",
                "cmake_minimum_required (VERSION 3.15.6)",
            )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "*COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rm(self, "*.cmake", os.path.join(self.package_folder, "include"))
        rmdir(self, os.path.join(self.package_folder, "include", "CMakeFiles"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "LibreSSL")
        self.cpp_info.set_property("pkg_config_name", "openssl")

        # Crypto
        self.cpp_info.components["crypto"].set_property("cmake_target_name", "LibreSSL::Crypto")
        self.cpp_info.components["crypto"].set_property("pkg_config_name", "libcrypto")
        self.cpp_info.components["crypto"].libs = [self._lib_name("crypto")]
        self.cpp_info.components["crypto"].resdirs = ["res"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["crypto"].system_libs = ["pthread", "rt"]
        elif self.settings.os == "SunOS":
            self.cpp_info.components["crypto"].system_libs = ["nsl", "socket"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["crypto"].system_libs = ["ws2_32"]
            if Version(self.version) >= "3.3.0":
                self.cpp_info.components["crypto"].system_libs.append("bcrypt")

        # SSL
        self.cpp_info.components["ssl"].set_property("cmake_target_name", "LibreSSL::SSL")
        self.cpp_info.components["ssl"].set_property("pkg_config_name", "libssl")
        self.cpp_info.components["ssl"].libs = [self._lib_name("ssl")]
        self.cpp_info.components["ssl"].resdirs = ["res"]
        self.cpp_info.components["ssl"].requires = ["crypto"]

        # TLS
        self.cpp_info.components["tls"].set_property("cmake_target_name", "LibreSSL::TLS")
        self.cpp_info.components["tls"].set_property("pkg_config_name", "libtls")
        self.cpp_info.components["tls"].libs = [self._lib_name("tls")]
        self.cpp_info.components["tls"].resdirs = ["res"]
        self.cpp_info.components["tls"].requires = ["crypto", "ssl"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "LibreSSL"
        self.cpp_info.names["cmake_find_package_multi"] = "LibreSSL"
        self.cpp_info.names["pkg_config"] = "openssl"
        self.cpp_info.components["crypto"].names["cmake_find_package"] = "Crypto"
        self.cpp_info.components["crypto"].names["cmake_find_package_multi"] = "Crypto"
        self.cpp_info.components["ssl"].names["cmake_find_package"] = "SSL"
        self.cpp_info.components["ssl"].names["cmake_find_package_multi"] = "SSL"
        self.cpp_info.components["tls"].names["cmake_find_package"] = "TLS"
        self.cpp_info.components["tls"].names["cmake_find_package_multi"] = "TLS"

    def _lib_name(self, name):
        libressl_version = Version(self.version)
        if self.settings.os == "Windows" and \
           (libressl_version >= "3.1.0" or (libressl_version < "3.1.0" and self.options.shared)):
            lib_fullpath = glob.glob(os.path.join(self.package_folder, "lib", f"*{name}*"))[0]
            lib_name = os.path.basename(lib_fullpath).split(".")[0].replace("lib", "")
            return lib_name
        return name
