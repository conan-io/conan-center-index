import os
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class LibCoapConan(ConanFile):
    name = "libcoap"
    license = "BSD-2-Clause"
    homepage = "https://github.com/obgm/libcoap"
    url = "https://github.com/conan-io/conan-center-index"
    description = """A CoAP (RFC 7252) implementation in C"""
    topics = ("coap")
    exports_sources = "CMakeLists.txt"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_epoll": [True, False],
        "dtls_backend": [None, "openssl", "gnutls", "tinydtls", "mbedtls"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_epoll": False,
        "dtls_backend": "openssl",
    }
    generators = "cmake", "cmake_find_package"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        if self.options.dtls_backend == "openssl":
            self.requires("openssl/1.1.1g")
        if self.options.dtls_backend == "mbedtls":
            self.requires("mbedtls/2.16.3-apache")
        if self.options.dtls_backend == "gnutls":
            raise ConanInvalidConfiguration("gnu tls not available yet")
        if self.options.dtls_backend == "tinydtls":
            raise ConanInvalidConfiguration("tinydtls not available yet")

    def _patch_files(self):
        # TODO: Remove custom targets when Conan components be available.
        if self.options.dtls_backend == "openssl":
            replace_ssl = 'OpenSSL::SSL'
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), replace_ssl, "OpenSSL::OpenSSL")
            replace_crypto = 'OpenSSL::Crypto'
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), replace_crypto, "OpenSSL::OpenSSL")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.os in ("Windows", "Macos"):
            raise ConanInvalidConfiguration("Platform is currently not supported")

        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + \
            os.path.basename(
                self.conan_data["sources"][self.version]["url"]).split(".")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["WITH_EPOLL"] = self.options.with_epoll
        self._cmake.definitions["ENABLE_DTLS"] = self.options.dtls_backend != None
        self._cmake.definitions["DTLS_BACKEND"] = self.options.dtls_backend
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_files()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder,
                                 "lib", "libcoap", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["coap"]
        if self.options.dtls_backend == None:
            self.cpp_info.names['pkg_config'] = "libcoap-2"
        else:
            self.cpp_info.names['pkg_config'] = "libcoap-2-{}".format(self.options.dtls_backend)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
