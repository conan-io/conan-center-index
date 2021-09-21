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

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9",
            "Visual Studio": "15.7",
            "clang": "7",
            "apple-clang": "11",
        }

    def validate(self):
        if not self.settings.compiler.get_safe("cppstd"):
            return

        if tools.Version(self.version) < "7.5.0":
            tools.check_min_cppstd(self, 11)
            return

        tools.check_min_cppstd(self, 17)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("{} requires C++17, which your compiler does not support.".format(self.name))
        else:
            self.output.warn("{} requires C++17. Your compiler is unknown. Assuming it supports C++17.".format(self.name))

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "src"))
