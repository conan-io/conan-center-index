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
            self.requires("openssl/1.1.1h")
        elif self.options.dtls_backend == "mbedtls":
            self.requires("mbedtls/2.16.3-apache")
        elif self.options.dtls_backend == "gnutls":
            raise ConanInvalidConfiguration("gnu tls not available yet")
        elif self.options.dtls_backend == "tinydtls":
            raise ConanInvalidConfiguration("tinydtls not available yet")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.os in ("Windows", "Macos"):
            raise ConanInvalidConfiguration("Platform is currently not supported")
        if self.options.shared:
            del self.options.fPIC
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
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        pkgconfig_filename = "libcoap-2{}".format("-{}".format(self.options.dtls_backend) if self.options.dtls_backend else "")
        self.cpp_info.names["pkg_config"] = pkgconfig_filename 
        self.cpp_info.components["coap"].names["cmake_find_package"] = "coap"
        self.cpp_info.components["coap"].names["cmake_find_package_multi"] = "coap"
        self.cpp_info.components["coap"].names["pkg_config"] = pkgconfig_filename
        self.cpp_info.components["coap"].libs = ["coap"]
        if self.settings.os == "Linux":
            self.cpp_info.components["coap"].system_libs = ["pthread"]
            if self.options.dtls_backend == "openssl":
                self.cpp_info.components["coap"].requires = ["openssl::openssl"]
            elif self.options.dtls_backend == "mbedtls":
                self.cpp_info.components["coap"].requires = ["mbedtls::mbedtls"]
