import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, load, save
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class MattiasgustavssonLibsConan(ConanFile):
    name = "mattiasgustavsson-libs"
    description = "Single-file public domain libraries for C/C++"
    license = ("Unlicense", "MIT")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mattiasgustavsson/libs"
    topics = ("utilities", "mattiasgustavsson", "libs", "header-only")

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
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _extract_licenses(self):
        header = load(self, os.path.join(self.source_folder, "thread.h"))
        mit_content = header[header.find("ALTERNATIVE A - ") : header.find("ALTERNATIVE B -")]
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE_MIT"), mit_content)
        unlicense_content = header[header.find("ALTERNATIVE B - ") : header.rfind("*/", 1)]
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE_UNLICENSE"), unlicense_content)

    def package(self):
        self._extract_licenses()
        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
