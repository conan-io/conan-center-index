from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.layout import basic_layout
from conan.tools.files import copy, get
import os


required_conan_version = ">=2.1"


class BoostWinTLS(ConanFile):
    name = "boost-wintls"
    description = "Native Windows TLS stream wrapper for use with boost::asio"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://wintls.dev"
    topics = (
        "header-only",
        "windows",
        "tls",
        "ssl",
        "networking",
        "boost",
        "asio",
        "sspi",
        "schannel",
    )
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"asio": ["boost", "standalone"]}
    default_options = {"asio": "boost"}

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.asio == "boost":
            self.requires("boost/1.86.0")
        else:
            self.requires("asio/1.32.0")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 14)
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} can only be used on Windows.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(
            self,
            "LICENSE",
            self.source_folder,
            os.path.join(self.package_folder, "licenses"),
        )
        copy(
            self,
            "*.hpp",
            os.path.join(self.source_folder, "include"),
            os.path.join(self.package_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        if self.options.asio == "boost":
            self.cpp_info.requires = ["boost::headers"]
        else:
            self.cpp_info.defines = ["ENABLE_WINTLS_STANDALONE_ASIO"]
        self.cpp_info.system_libs = ["crypt32", "secur32", "ws2_32", "wsock32"]
