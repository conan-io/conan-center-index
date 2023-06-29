import os

from conan import ConanFile
from conan.tools.files import copy, get, load, save
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class CuteHeadersConan(ConanFile):
    name = "cute_headers"
    description = ("Various single-file cross-platform C/C++ "
                   "headers implementing self-contained libraries.")
    license = "Unlicense"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/RandyGaul/cute_headers"
    topics = ("various", "pure-c", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _extract_license(self):
        file = os.path.join(self.source_folder, "include/cute_math2d.h")
        file_content = load(self, file)
        license_content = file_content[file_content.rfind("/*") :]
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_content)

    def package(self):
        self._extract_license()
        copy(self,
             pattern="*.h",
             dst=os.path.join(self.package_folder, "include"),
             src=self.source_folder,
             excludes=("examples_cute_*", "test_cute_*"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
