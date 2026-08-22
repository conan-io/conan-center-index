import os

from conan import ConanFile
from conan.tools.files import copy, get, load, save
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class PanziPortableEndian(ConanFile):
    name = "panzi-portable-endian"
    description = ("This provides the endian conversion functions from "
                   "endian.h on Windows, Linux, *BSD, and Mac OS X")
    license = "LicenseRef-panzi-portable-endian-public-domain"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gist.github.com/panzi/6856583"
    topics = ("endian", "header-only")

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
        header = load(self, os.path.join(self.source_folder, "portable_endian.h"))
        license_contents = header[0: (header.find("#ifndef", 1))]
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_contents)

    def package(self):
        self._extract_license()
        copy(self, "*.h", dst=os.path.join(self.package_folder, "include"), src=self.source_folder, keep_path=False)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
