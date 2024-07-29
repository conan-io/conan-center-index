from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os


required_conan_version = ">=1.52.0"


class IpAddressConan(ConanFile):
    name = "ipaddress"
    description = "A library for working and manipulating IPv4/IPv6 addresses and networks"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/VladimirShaleev/ipaddress"
    topics = ("ipv4", "ipv6", "ipaddress", "ip", "network", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    options = {
        "exceptions": [True, False],
        "overload_std": [True, False],
        "ipv6_scope": [True, False],
        "ipv6_scope_max_length": ["ANY"],
    }
    default_options = {
        "exceptions": True,
        "overload_std": True,
        "ipv6_scope": True,
        "ipv6_scope_max_length": 16,
    }

    @property
    def _min_cppstd(self):
        return 11

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "13.0",
            "clang": "6.0",
            "gcc": "7.5",
            "msvc": "192",
            "Visual Studio": "16",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} doesn't support {self.settings.compiler} < {minimum_version}"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(
            self,
            "*.hpp",
            os.path.join(self.source_folder, "include"),
            os.path.join(self.package_folder, "include")
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        if not self.options.exceptions:
            self.cpp_info.defines.append("IPADDRESS_NO_EXCEPTIONS")
        if not self.options.overload_std:
            self.cpp_info.defines.append("IPADDRESS_NO_OVERLOAD_STD")
        if not self.options.ipv6_scope:
            self.cpp_info.defines.append("IPADDRESS_NO_IPV6_SCOPE")
        else:
            self.cpp_info.defines.append(f"IPADDRESS_IPV6_SCOPE_MAX_LENGTH={int(self.options.ipv6_scope_max_length)}")
