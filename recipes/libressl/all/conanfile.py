from conan.tools.microsoft import msvc_runtime_flag
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import glob
import os

required_conan_version = ">=1.43.0"


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

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.options.shared and self._is_msvc and "MT" in msvc_runtime_flag(self):
            raise ConanInvalidConfiguration("Static runtime linked into shared LibreSSL not supported")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)
        if tools.Version(self.version) >= "3.1.1":
            tools.replace_in_file(
                    os.path.join(self._source_subfolder, "CMakeLists.txt"),
                    "cmake_minimum_required (VERSION 3.16.4)",
                    "cmake_minimum_required (VERSION 3.15.6)"
            )

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["LIBRESSL_SKIP_INSTALL"] = False
        self._cmake.definitions["LIBRESSL_APPS"] = False # Warning: if enabled, do not use cmake installation, to avoid installing files in OPENSSLDIR
        self._cmake.definitions["LIBRESSL_TESTS"] = False
        self._cmake.definitions["ENABLE_ASM"] = True
        self._cmake.definitions["ENABLE_EXTRATESTS"] = False
        self._cmake.definitions["ENABLE_NC"] = False
        self._cmake.definitions["OPENSSLDIR"] = os.path.join(self.package_folder, "res")
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("*COPYING", dst="licenses", keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()
        tools.remove_files_by_mask(os.path.join(self.package_folder, "include"), "*.cmake")
        tools.rmdir(os.path.join(self.package_folder, "include", "CMakeFiles"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "LibreSSL")
        self.cpp_info.set_property("pkg_config_name", "openssl")

        # Crypto
        self.cpp_info.components["crypto"].set_property("cmake_target_name", "LibreSSL::Crypto")
        self.cpp_info.components["crypto"].set_property("pkg_config_name", "libcrypto")
        self.cpp_info.components["crypto"].libs = [self._lib_name("crypto")]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["crypto"].system_libs = ["pthread", "rt"]
        elif self.settings.os == "SunOS":
            self.cpp_info.components["crypto"].system_libs = ["nsl", "socket"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["crypto"].system_libs = ["ws2_32"]
            if tools.Version(self.version) >= "3.3.0":
                self.cpp_info.components["crypto"].system_libs.append("bcrypt")

        # SSL
        self.cpp_info.components["ssl"].set_property("cmake_target_name", "LibreSSL::SSL")
        self.cpp_info.components["ssl"].set_property("pkg_config_name", "libssl")
        self.cpp_info.components["ssl"].libs = [self._lib_name("ssl")]
        self.cpp_info.components["ssl"].requires = ["crypto"]

        # TLS
        self.cpp_info.components["tls"].set_property("cmake_target_name", "LibreSSL::TLS")
        self.cpp_info.components["tls"].set_property("pkg_config_name", "libtls")
        self.cpp_info.components["tls"].libs = [self._lib_name("tls")]
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
        libressl_version = tools.Version(self.version)
        if self.settings.os == "Windows" and \
           (libressl_version >= "3.1.0" or (libressl_version < "3.1.0" and self.options.shared)):
            lib_fullpath = glob.glob(os.path.join(self.package_folder, "lib", "*{}*".format(name)))[0]
            lib_name = os.path.basename(lib_fullpath).split(".")[0].replace("lib", "")
            return lib_name
        return name
