import os
from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration

class SeqanConan(ConanFile):
    name = "seqan"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/seqan/seqan"
    description = """
SeqAn is an open source C++ library of efficient algorithms and data structures for the analysis of sequences 
with the focus on biological data. Our library applies a unique generic design that guarantees high performance, 
generality, extensibility, and integration with other libraries. 
SeqAn is easy to use and simplifies the development of new software tools with a minimal loss of performance.
"""
    topics = ("conan", "cpp98", "cpp11", "cpp14", "cpp17",
              "algorithms", "data structures", "biological sequences")
    license = "BSD-3-Clause"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "Visual Studio": "14",
            "clang": "3.4",
            "apple-clang": "3.4"
        }

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 14)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("seqan requires C++14, which your compiler does not fully support.")
        else:
            self.output.warn("seqan requires C++14. Your compiler is unknown. Assuming it supports C++14.")


    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "seqan-seqan-v" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("*", dst="include",
                  src=os.path.join(self._source_subfolder, "include"), keep_path=True)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
