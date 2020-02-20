import os
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class LibCoapConan(ConanFile):
    name = "libcoap"
    license = "BSD-2-Clause"
    homepage = "https://github.com/gocarlos/libcoap/"
    url = "https://github.com/conan-io/conan-center-index"
    description = """A CoAP (RFC 7252) implementation in C"""
    topics = ("coap")
    exports_sources = "CMakeLists.txt"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_dtls": [True, False],
        "with_openssl": [True, False],
        "with_gnutls": [True, False],
        "with_tinydtls": [True, False],
        "with_mbedtls": [True, False],
        "with_epoll": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_dtls": True,
        "with_openssl": True,
        "with_gnutls": False,
        "with_tinydtls": False,
        "with_mbedtls": False,
        "with_epoll": False,
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
        if self.options.enable_dtls and self.options.with_openssl:
            self.requires.add("openssl/1.1.1d")
        if self.options.enable_dtls and self.options.with_mbedtls:
            self.requires.add("mbedtls/2.16.3-apache")
        if self.options.enable_dtls and self.options.with_gnutls:
            raise ConanInvalidConfiguration("gnu tls not available yet")
        if self.options.enable_dtls and self.options.with_tinydtls:
            raise ConanInvalidConfiguration("tinydtls not available yet")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
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
        self._cmake.definitions["ENABLE_DTLS"] = self.options.enable_dtls
        self._cmake.definitions["WITH_OPENSSL"] = self.options.with_openssl
        self._cmake.definitions["WITH_GNUTLS"] = self.options.with_gnutls
        self._cmake.definitions["WITH_TINYDTLS"] = self.options.with_tinydtls
        self._cmake.definitions["WITH_EPOLL"] = self.options.with_epoll
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst='licenses', src=os.path.join(
            self._source_subfolder, "license"))
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder,
                                 "lib", "libcoap", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["coap"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
