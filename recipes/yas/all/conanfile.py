import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, load, save
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class YasConan(ConanFile):
    name = "yas"
    description = "Yet Another Serialization"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/niXman/yas"
    topics = ("serialization", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 11

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _extract_license(self):
        header = load(self, os.path.join(self.source_folder, "include", "yas", "binary_oarchive.hpp"))
        license_contents = header[: header.find("#")].replace("//", "").replace("\n ", "\n").lstrip()
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_contents)

    def package(self):
        self._extract_license()
        copy(self, "*",
             dst=os.path.join(self.package_folder, "include"),
             src=os.path.join(self.source_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
