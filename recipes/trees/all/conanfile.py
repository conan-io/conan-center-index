import os
from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=2.0.0"


class TreesConan(ConanFile):
    name = "trees"
    description = "Extensible tree data structure."
    license = "MIT"

    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/JoelLefkowitz/trees"
    author = "Joel Lefkowitz (joellefkowitz@hotmail.com)"

    topics = (
        "tree",
        "graph",
        "degrees",
        "node",
        "header-only",
    )

    settings = (
        "os",
        "arch",
        "compiler",
        "build_type",
    )

    package_type = "header-library"
    no_copy_source = True

    requires = ("funky/0.3.0",)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(
            self,
            **self.conan_data["sources"][self.version],
            strip_root=True,
        )

    def build(self):
        pass

    def package(self):
        copy(
            self,
            "LICENSE.md",
            self.source_folder,
            os.path.join(self.package_folder, "licenses"),
        )
        copy(
            self,
            "*.[ht]pp",
            os.path.join(self.source_folder, "src"),
            os.path.join(self.package_folder, "include", self.name),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
