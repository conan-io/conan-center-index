from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class BitmagicConan(ConanFile):
    name = "bitmagic"
    description = "BitMagic Library helps to develop high-throughput intelligent search systems, " \
                  "promote combination of hardware optimizations and on the fly compression to fit " \
                  "inverted indexes and binary fingerprints into memory, minimize disk and network footprint."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://bitmagic.io"
    topics = ("information-retrieval", "algorithm", "bit-manipulation",
              "integer-compression", "sparse-vector", "sparse-matrix", "bit-array",
              "bit-vector", "indexing-engine", "adjacency-matrix", "associative-array")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
        }

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 17)
        minimum_version = self._minimum_compilers_version.get(str(self.info.settings.compiler), False)
        if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.name} requires C++17, which your compiler does not support.")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", src=os.path.join(self.source_folder, "src"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
