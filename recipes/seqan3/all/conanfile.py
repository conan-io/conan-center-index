import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class Seqan3Conan(ConanFile):
    name = "seqan3"
    description = "SeqAn3 is the new version of the popular SeqAn template library for the analysis of biological sequences."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/seqan/seqan3"
    topics = ("cpp20", "algorithms", "data structures", "biological sequences", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {"gcc": "10"}

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler != "gcc":
            raise ConanInvalidConfiguration("SeqAn3 only supports GCC.")

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("SeqAn3 requires C++20, which your compiler does not fully support.")
        else:
            self.output.warning("SeqAn3 requires C++20. Your compiler is unknown. Assuming it supports C++20.")

        if self.settings.compiler == "gcc" and self.settings.compiler.libcxx != "libstdc++11":
            self.output.warning("SeqAn3 does not actively support libstdc++, consider using libstdc++11 instead.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "*", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"), keep_path=True)
        copy(self, "LICENSE.md", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        for submodule in ["range-v3", "cereal", "sdsl-lite"]:
            copy(self, "*.hpp",
                 dst=os.path.join(self.package_folder, "include"),
                 src=os.path.join(self.source_folder, "submodules", submodule, "include"),
                 keep_path=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "seqan3")
        self.cpp_info.set_property("cmake_target_name", "seqan3::seqan3")
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
