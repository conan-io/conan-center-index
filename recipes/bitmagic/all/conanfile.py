from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class BitmagicConan(ConanFile):
    name = "bitmagic"
    description = "BitMagic Library helps to develop high-throughput intelligent search systems, " \
                  "promote combination of hardware optimizations and on the fly compression to fit " \
                  "inverted indexes and binary fingerprints into memory, minimize disk and network footprint."
    license = "Apache-2.0"
    topics = ("bitmagic", "information-retrieval", "algorithm", "bit-manipulation",
              "integer-compression", "sparse-vector", "sparse-matrix", "bit-array",
              "bit-vector", "indexing-engine", "adjacency-matrix", "associative-array")
    homepage = "http://bitmagic.io"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def _minimum_compilers_version(self, cppstd):
        standards = {
            "11": {
                "Visual Studio": "15",
                "gcc": "4.8",
                "clang": "4",
                "apple-clang": "9",
            },
            "17": {
                "Visual Studio": "16",
                "gcc": "7",
                "clang": "6",
                "apple-clang": "10",
            },
        }
        return standards.get(cppstd) or {}

    @property
    def _cppstd(self):
        return "11" if tools.Version(self.version) < "7.5.0" else "17"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._cppstd)

        minimum_version = self._minimum_compilers_version(self._cppstd).get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("{} requires C++{}, which your compiler does not support.".format(self.name, self._cppstd))
        else:
            self.output.warn("{0} requires C++{1}. Your compiler is unknown. Assuming it supports C++{1}.".format(self.name, self._cppstd))

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "src"))
