from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os


required_conan_version = ">=1.54.0"


class UvwConan(ConanFile):
    name = "uvw"
    description = "Header-only, event based, tiny and easy to use libuv wrapper in modern C++."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/skypjack/uvw"
    topics = ("libuv", "io", "networking", "header-only",)
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "191",
            "gcc": "7",
            "clang": "5",
            "apple-clang": "10",
        }

    @property
    def _required_libuv_version(self):
        return {
            "3.2.0": "1.46.0",
            "3.1.0": "1.45.0",
            "2.12.1": "1.44.2",
            "2.11.0": "1.43.0",
            "2.10.0": "1.42.0",
        }[self.version]

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires(f"libuv/{self._required_libuv_version}")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("{self.ref} requires C++{self._min_cppstd}, which your compiler doesn't support")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "src"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "*", src=os.path.join(self.source_folder, "src", "uvw"), dst=os.path.join(self.package_folder, "include", "uvw"))
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
