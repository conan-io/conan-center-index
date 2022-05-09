import os
import conan.tools.files
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration

class SeqanConan(ConanFile):
    name = "seqan3"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/seqan/seqan3"
    description = "SeqAn3 is the new version of the popular SeqAn template library for the analysis of biological sequences."
    topics = ("cpp20", "algorithms", "data structures", "biological sequences")
    license = "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "10"
        }

    def configure(self):
        if self.settings.compiler != "gcc":
            raise ConanInvalidConfiguration("SeqAn3 only supports GCC.")

        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 20)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("SeqAn3 requires C++20, which your compiler does not fully support.")
        else:
            self.output.warn("SeqAn3 requires C++20. Your compiler is unknown. Assuming it supports C++20.")

        if self.settings.compiler == "gcc" and self.settings.compiler.libcxx != "libstdc++11":
            self.output.warn("SeqAn3 does not actively support libstdc++, consider using libstdc++11 instead.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "seqan3-" + self.version + "-Source"
        conan.tools.files.rename(self, extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("*", dst="include",
                  src=os.path.join(self._source_subfolder, "include"), keep_path=True)
        for submodule in ["range-v3", "cereal", "sdsl-lite"]:
            self.copy("*.hpp", dst="include",
                  src=os.path.join(self._source_subfolder, "submodules", submodule, "include"), keep_path=True)
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "seqan3"
        self.cpp_info.names["cmake_find_package_multi"] = "seqan3"
