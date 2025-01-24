import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=2.1"


class ProxyConan(ConanFile):
    name = "proxy"
    description = "Proxy: Next Generation Polymorphism in C++"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/microsoft/proxy"
    topics = ("runtime-polymorphism", "polymorphism", "duck-typing", "metaprogramming", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _compilers_minimum_version(self):
        """ Actual compiler support based on upstream's README.md """
        return {
            # proxy/2.3.0 has an internal compilation error on gcc 11.
            "gcc": "11" if Version(self.version) < "2.3.0" else "12",
            "clang": "15",
            "apple-clang": "14",
            "msvc": "193",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 20)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires at least {self.settings.compiler} {minimum_version}"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "proxy.h", self.source_folder, os.path.join(self.package_folder, "include", "proxy"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "proxy")
        self.cpp_info.set_property("cmake_target_name", "msft_proxy")

        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
