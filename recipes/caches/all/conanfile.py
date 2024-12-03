import os
from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=2.0.0"


class CachesConan(ConanFile):
    name = "caches"
    description = "Extensible cache templates."

    version = "0.4.0"
    license = "MIT"

    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/JoelLefkowitz/caches"

    topics = (
        "cache",
        "fifo",
        "lifo",
        "lru",
        "header-only",
    )

    package_type = "header-library"
    generators = "SConsDeps"

    source_patterns = [
        "LICENSE.md",
        "src/*.[cht]pp",
    ]

    package_patterns = {
        "LICENSE.md": "licenses",
        "*.[ht]pp": "include/caches",
    }

    def layout(self):
        basic_layout(self, "src")

    def requirements(self):
        self.test_requires("gtest/1.12.1")

    def package_id(self):
        self.info.clear()

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

    def source(self):
        if self.conan_data:
            get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def export_sources(self):
        for source in self.source_patterns:
            copy(self, source, self.recipe_folder, self.export_sources_folder)

    def package(self):
        for k, v in self.package_patterns.items():
            copy(self, k, self.source_folder, os.path.join(self.package_folder, v))
