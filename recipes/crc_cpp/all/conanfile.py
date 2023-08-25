from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.scm import Version
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration
import os


required_conan_version = ">=1.54.0"


class Crc_CppConan(ConanFile):
    name = "crc_cpp"
    description = "A header only constexpr / compile time small-table based CRC library for C++17 and newer"
    topics = ("crc", "constexpr", "cpp17", "cpp20", "header-only")
    settings = "os", "arch", "compiler", "build_type"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/AshleyRoll/crc_cpp"
    license = "MIT"
    package_type = "header-library"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "14.1",
            "gcc": "9",
            "clang": "5",
            "apple-clang": "10",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="*", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
