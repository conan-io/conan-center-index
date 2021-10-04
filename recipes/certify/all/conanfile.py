from conans import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class CertifyConan(ConanFile):
    name = "certify"
    description = "Platform-specific TLS keystore abstraction for use with Boost.ASIO and OpenSSL"
    topics = ("conan", "boost", "asio", "tls", "ssl", "https")
    url = "https://github.com/djarek/certify"
    homepage = "https://djarek.github.io/certify/"
    license = "BSL-1.0"
    settings = "compiler"
    generators = "cmake", "cmake_find_package"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _min_cppstd(self):
        return "17"

    def requirements(self):
        self.requires("boost/1.76.0")
        self.requires("openssl/1.1.1k")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._min_cppstd)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE_1_0.txt", dst="licenses",
                  src=self._source_subfolder)
        self.copy(pattern="*", dst="include",
                  src=os.path.join(self._source_subfolder, "include"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "certify"
        self.cpp_info.names["cmake_find_package_multi"] = "certify"
        self.cpp_info.names["pkg_config"] = "certify"
