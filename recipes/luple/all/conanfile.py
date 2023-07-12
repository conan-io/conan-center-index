from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, download, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class LupleConan(ConanFile):
    name = "luple"
    license = "Public-domain"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/alexpolt/luple"
    description = "Home to luple, nuple, C++ String Interning, Struct Reader and C++ Type Loophole"
    topics = ("loophole", "luple", "nuple", "struct", "intern")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    package_type = "header-library"

    @property
    def _min_cppstd(self):
        return "14"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "10",
            "Visual Studio": "14",
            "msvc": "190",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and loose_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version][0],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        # This package doesn't have a license file, it is public domain declared in the Readme
        copy(self, "README.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
