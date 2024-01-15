from conan import ConanFile
from conan.tools.files import get, copy, load, save
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=1.52.0"


class CuteHeadersConan(ConanFile):
    name = "cute_headers"
    description = "Various single-file cross-platform C/C++ headers implementing self-contained libraries."
    topics = ("various", "pure-c")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/RandyGaul/cute_headers"
    license = "Unlicense"
    package_type = "header-library"
    no_copy_source = True

    def _extract_license(self):
        file = os.path.join(self.package_folder, "include", "cute_math2d.h")
        file_content = load(self, file)
        return file_content[file_content.rfind('/*'):]

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(
            self,
            pattern="*.h",
            dst=os.path.join(self.package_folder, "include"),
            src=self.source_folder,
            excludes=("examples_cute_*", "test_cute_*")
        )
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._extract_license())

    def package_id(self):
        self.info.clear()

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
