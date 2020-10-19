from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class MortonndConan(ConanFile):
    name = "morton-nd"
    description = "A header-only Morton encode/decode library (C++14) capable " \
                  "of encoding from and decoding to N-dimensional space."
    license = "MIT"
    topics = ("conan", "morton-nd", "morton", "encoding", "decoding", "n-dimensional")
    homepage = "https://github.com/kevinhartman/morton-nd"
    url = "https://github.com/conan-io/conan-center-index"
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
            "apple-clang": "5.1",
        }

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 14)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("morton-nd requires C++14. Your compiler is unknown. Assuming it supports C++14.")
        elif tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("morton-nd requires C++14, which your compiler does not support.")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "morton-nd"
        self.cpp_info.names["cmake_find_package_multi"] = "morton-nd"
        self.cpp_info.components["mortonnd"].names["cmake_find_package"] = "MortonND"
        self.cpp_info.components["mortonnd"].names["cmake_find_package_multi"] = "MortonND"
