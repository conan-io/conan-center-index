from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class Libssh2Conan(ConanFile):
    name = "libssh2"
    description = "libssh2 is a client-side C library implementing the SSH2 protocol"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libssh2.org"
    topics = ("libssh", "ssh", "shell", "ssh2", "connection")
    license = "BSD-3-Clause"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"
    _source_subfolder = "source_subfolder"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zlib": [True, False],
        "enable_crypt_none": [True, False],
        "enable_mac_none": [True, False],
        "crypto_backend": ["openssl", "mbedtls"],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zlib": True,
        "enable_crypt_none": False,
        "enable_mac_none": False,
        "crypto_backend": "openssl",
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libssh2-%s" % (self.version), self._source_subfolder)

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.crypto_backend == "openssl":
            self.requires("openssl/1.1.1f")
        elif self.options.crypto_backend == "mbedtls":
            self.requires("mbedtls/2.16.3-gpl")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['ENABLE_ZLIB_COMPRESSION'] = self.options.with_zlib
        cmake.definitions['ENABLE_CRYPT_NONE'] = self.options.enable_crypt_none
        cmake.definitions['ENABLE_MAC_NONE'] = self.options.enable_mac_none
        if self.options.crypto_backend == "openssl":
            cmake.definitions['CRYPTO_BACKEND'] = 'OpenSSL'
            cmake.definitions['OPENSSL_ROOT_DIR'] = self.deps_cpp_info['openssl'].rootpath
        elif self.options.crypto_backend == "mbedtls":
            cmake.definitions['CRYPTO_BACKEND'] = "mbedTLS"
        else:
            raise ConanInvalidConfiguration("Crypto backend must be specified")

        cmake.definitions['BUILD_EXAMPLES'] = False
        cmake.definitions['BUILD_TESTING'] = False
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy("COPYING", dst="licenses", src=self._source_subfolder, keep_path=False)
        if os.path.exists(os.path.join(self.package_folder, 'lib64')):
            # rhel installs libraries into lib64
            os.rename(os.path.join(self.package_folder, 'lib64'),
                      os.path.join(self.package_folder, 'lib'))

        tools.rmdir(os.path.join(self.package_folder, 'share'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'cmake'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        lib_name = "libssh2" if self.settings.os == "Windows" else "ssh2"
        self.cpp_info.libs = [lib_name]

        if self.settings.compiler == "Visual Studio" and not self.options.shared:
            self.cpp_info.system_libs.append('ws2_32')
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(['pthread', 'dl'])
