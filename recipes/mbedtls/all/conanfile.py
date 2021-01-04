from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
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
    options = {"shared": [True, False], "fPIC": [True, False], "with_zlib": [True, False]}
    default_options = {"shared": False, "fPIC": True, "with_zlib": True}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _version(self):
        return self.version.rsplit("-", 1)[0]

    @property
    def _license(self):
        return self.version.rsplit("-", 1)[1]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx
        if tools.Version(self.version) >= "2.23.0":
            self.license = "Apache-2.0"

        if tools.Version(self.version) >= "2.23.0" \
            and self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration(
                "{}/{} does not support shared build on Windows".format(self.name, self.version))

        if tools.Version(self.version) >= "2.23.0" \
            and self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "5":
            # The command line flags set are not supported on older versions of gcc
            raise ConanInvalidConfiguration("{}-{} is not supported by this recipe".format(self.settings.compiler, self.settings.compiler.version))

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "{}-{}".format(self.name, self._version)
        if tools.Version(self.version) >= "2.23.0": # went to mbedtls-mbedtls-X.X.X
            extracted_dir = "{}-{}".format(self.name, extracted_dir)
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["USE_SHARED_MBEDTLS_LIBRARY"] = self.options.shared
            self._cmake.definitions["USE_STATIC_MBEDTLS_LIBRARY"] = not self.options.shared
            self._cmake.definitions["ENABLE_ZLIB_SUPPORT"] = self.options.with_zlib
            self._cmake.definitions["ENABLE_PROGRAMS"] = False
            self._cmake.definitions["ENABLE_TESTING"] = False
            self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=os.path.join(self.source_folder, self._source_subfolder), dst="licenses")
        if tools.Version(self.version) < "2.23.0": # less then 2.23 is multi-licensed
            if self._license == "gpl":
                self.copy("gpl-2.0.txt", src=os.path.join(self.source_folder, self._source_subfolder), dst="licenses")
            else:
                self.copy("apache-2.0.txt", src=os.path.join(self.source_folder, self._source_subfolder), dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        # https://gitlab.kitware.com/cmake/cmake/blob/de7c21d677db1ddaeece03c19e13e448f4031511/CMakeLists.txt#L380
        self.cpp_info.names["cmake_find_package"] = "MbedTLS"
        self.cpp_info.names["cmake_find_package_multi"] = "MbedTLS"
        self.cpp_info.libs = ["mbedtls", "mbedx509", "mbedcrypto"]
