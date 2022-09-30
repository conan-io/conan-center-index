from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


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
    def _min_cppstd(self):
        return "14"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "Visual Studio": "14",
            "msvc": "190",
            "clang": "3.4",
            "apple-clang": "5.1",
        }

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.name} {self.version} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "morton-nd")
        self.cpp_info.set_property("cmake_target_name", "morton-nd::MortonND")
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.names["cmake_find_package"] = "morton-nd"
        self.cpp_info.names["cmake_find_package_multi"] = "morton-nd"
        self.cpp_info.components["mortonnd"].names["cmake_find_package"] = "MortonND"
        self.cpp_info.components["mortonnd"].names["cmake_find_package_multi"] = "MortonND"
        self.cpp_info.components["mortonnd"].set_property("cmake_target_name", "morton-nd::MortonND")
        self.cpp_info.components["mortonnd"].bindirs = []
        self.cpp_info.components["mortonnd"].frameworkdirs = []
        self.cpp_info.components["mortonnd"].libdirs = []
        self.cpp_info.components["mortonnd"].resdirs = []
