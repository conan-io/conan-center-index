from conans import ConanFile, tools
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

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "src"))
