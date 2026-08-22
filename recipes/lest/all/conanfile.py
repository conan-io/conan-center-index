import os

from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout


class LestConan(ConanFile):
    name = "lest"
    description = (
        "A modern, C++11-native, single-file header-only, "
        "tiny framework for unit-tests, TDD and BDD."
    )
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/martinmoene/lest"
    topics = ("testing", "testing-framework", "unit-testing", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(
            self,
            "LICENSE.txt",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        copy(
            self,
            pattern="*.hpp",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
