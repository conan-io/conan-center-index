import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class CertifyConan(ConanFile):
    name = "certify"
    description = "Platform-specific TLS keystore abstraction for use with Boost.ASIO and OpenSSL"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/djarek/certify"
    topics = ("boost", "asio", "tls", "ssl", "https", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9",
            "Visual Studio": "15.7",
            "clang": "7",
            "apple-clang": "11",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.83.0")
        self.requires("openssl/[>=1.1 <4]")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warning(
                f"{self.name} requires C++17. Your compiler is unknown. Assuming it supports C++17."
            )
        elif lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                f"{self.name} requires C++17, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(
            self,
            pattern="LICENSE_1_0.txt",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        copy(
            self,
            pattern="*",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "certify")
        self.cpp_info.set_property("cmake_target_name", "certify::core")

        self.cpp_info.components["_certify"].requires = ["boost::boost", "openssl::openssl"]
        self.cpp_info.components["_certify"].names["cmake_find_package"] = "core"
        self.cpp_info.components["_certify"].names["cmake_find_package_multi"] = "core"

        self.cpp_info.names["cmake_find_package"] = "certify"
        self.cpp_info.names["cmake_find_package_multi"] = "certify"
