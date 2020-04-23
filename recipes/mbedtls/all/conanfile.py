from conans import CMake, ConanFile, tools
import os


class MBedTLSConan(ConanFile):
    name = "mbedtls"
    description = "mbed TLS makes it trivially easy for developers to include cryptographic and SSL/TLS capabilities in their (embedded) products"
    topics = ("conan", "mbedtls", "polarssl", "tls", "security")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://tls.mbed.org"
    license = ("GPL-2.0", "Apache-2.0",)
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zlib": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zlib": True,
    }
    _source_subfolder = "source_subfolder"

    @property
    def _version(self):
        return self.version.rsplit("-", 1)[0]

    @property
    def _license(self):
        return self.version.rsplit("-", 1)[1]

    def config_options(self):
        if self.settings.os == "Windows" or self.options.shared:
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "{}-{}".format(self.name, self._version)
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["USE_SHARED_MBEDTLS_LIBRARY"] = self.options.shared
        cmake.definitions["USE_STATIC_MBEDTLS_LIBRARY"] = not self.options.shared
        cmake.definitions["ENABLE_ZLIB_SUPPORT"] = self.options.with_zlib
        cmake.definitions["ENABLE_PROGRAMS"] = False
        cmake.definitions["ENABLE_TESTING"] = False

        cmake.configure()

        return cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=os.path.join(self.source_folder, self._source_subfolder), dst="licenses")
        if self._license == "gpl":
            self.copy("gpl-2.0.txt", src=os.path.join(self.source_folder, self._source_subfolder), dst="licenses")
        else:
            self.copy("apache-2.0.txt", src=os.path.join(self.source_folder, self._source_subfolder), dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "MbedTLS"
        self.cpp_info.names["cmake_find_package_multi"] = "MbedTLS"
        self.cpp_info.libs = ["mbedtls", "mbedx509", "mbedcrypto", ]
