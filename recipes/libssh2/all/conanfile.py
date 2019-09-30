#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

class Libssh2Conan(ConanFile):
    name = "libssh2"

    description = "libssh2 is a client-side C library implementing the SSH2 protocol"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libssh2.org"
    license = "BSD 3-Clause"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    _source_subfolder = "source_subfolder"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zlib": [True, False],
        "enable_crypt_none": [True, False],
        "enable_mac_none": [True, False],
        "with_openssl": [True, False]
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zlib": True,
        "enable_crypt_none": False,
        "enable_mac_none": False,
        "with_openssl": True
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libssh2-%s" % (self.version), self._source_subfolder)

    def configure(self):
        del self.settings.compiler.libcxx

    def requirements(self):
        if self.options.with_zlib:
            self.requires.add("zlib/1.2.11")
        if self.options.with_openssl:
            self.requires.add("openssl/1.0.2t")

    def build(self):
        cmake = CMake(self)

        cmake.definitions['BUILD_SHARED_LIBS'] = self.options.shared
        cmake.definitions['ENABLE_ZLIB_COMPRESSION'] = self.options.with_zlib
        cmake.definitions['ENABLE_CRYPT_NONE'] = self.options.enable_crypt_none
        cmake.definitions['ENABLE_MAC_NONE'] = self.options.enable_mac_none
        if self.options.with_openssl:
            cmake.definitions['CRYPTO_BACKEND'] = 'OpenSSL'
            cmake.definitions['OPENSSL_ROOT_DIR'] = self.deps_cpp_info['openssl'].rootpath
        else:
            raise ConanInvalidConfiguration("Crypto backend must be specified")
        cmake.definitions['BUILD_EXAMPLES'] = False
        cmake.definitions['BUILD_TESTING'] = False

        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder, keep_path=False)
        if os.path.exists(os.path.join(self.package_folder, 'lib64')):
            # rhel installs libraries into lib64
            os.rename(os.path.join(self.package_folder, 'lib64'),
                      os.path.join(self.package_folder, 'lib'))

        tools.rmdir(os.path.join(self.package_folder, 'share'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'cmake'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        self.cpp_info.libs = ["ssh2"]

        if self.settings.compiler == "Visual Studio":
            if not self.options.shared:
                self.cpp_info.libs.append('ws2_32')
