from conan import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class MortonndConan(ConanFile):
    name = "morton-nd"
    description = "A header-only Morton encode/decode library (C++14) capable " \
                  "of encoding from and decoding to N-dimensional space."
    license = "MIT"
    topics = ("morton-nd", "morton", "encoding", "decoding", "n-dimensional")
    homepage = "https://github.com/kevinhartman/morton-nd"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
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

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, 14)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("morton-nd requires C++14. Your compiler is unknown. Assuming it supports C++14.")
        elif tools.scm.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("morton-nd requires C++14, which your compiler does not support.")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "morton-nd")
        self.cpp_info.set_property("cmake_target_name", "morton-nd::MortonND")

        self.cpp_info.names["cmake_find_package"] = "morton-nd"
        self.cpp_info.names["cmake_find_package_multi"] = "morton-nd"
        self.cpp_info.components["mortonnd"].names["cmake_find_package"] = "MortonND"
        self.cpp_info.components["mortonnd"].names["cmake_find_package_multi"] = "MortonND"
        self.cpp_info.components["mortonnd"].set_property("cmake_target_name", "morton-nd::MortonND")
