import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=1.50.0"


class ClippConan(ConanFile):
    name = "clipp"
    description = (
        "Easy to use, powerful & expressive command line argument parsing "
        "for modern C++ / single header / usage & doc generation."
    )
    topics = ("argparse", "cli", "usage", "options", "subcommands")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/muellan/clipp"
    license = "MIT"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return "11"

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "clipp")
        self.cpp_info.set_property("cmake_target_name", "clipp::clipp")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
