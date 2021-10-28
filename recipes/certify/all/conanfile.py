from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class CertifyConan(ConanFile):
    name = "certify"
    description = "Platform-specific TLS keystore abstraction for use with Boost.ASIO and OpenSSL"
    topics = ("boost", "asio", "tls", "ssl", "https")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/djarek/certify"
    license = "BSL-1.0"
    settings = "compiler"
    generators = "cmake", "cmake_find_package"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9",
            "Visual Studio": "15.7",
            "clang": "7",
            "apple-clang": "11",
        }

    @property
    def _min_cppstd(self):
        return "17"

    def requirements(self):
        self.requires("boost/1.77.0")
        self.requires("openssl/1.1.1l")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("{} requires C++17, which your compiler does not support.".format(self.name))
        else:
            self.output.warn("{} requires C++17. Your compiler is unknown. Assuming it supports C++17.".format(self.name))

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
