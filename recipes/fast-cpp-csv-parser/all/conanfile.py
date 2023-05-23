from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class FastcppcsvparserConan(ConanFile):
    name = "fast-cpp-csv-parser"
    description = "C++11 header-only library for reading comma separated value (CSV) files."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ben-strasser/fast-cpp-csv-parser"
    topics = ("csv", "parser", "header-only")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_thread": [True, False],
    }
    default_options = {
        "with_thread": True,
    }

    no_copy_source = True

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "csv.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include", "fast-cpp-csv-parser"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs.append(os.path.join("include", "fast-cpp-csv-parser"))
        if not self.options.with_thread:
            self.cpp_info.defines.append("CSV_IO_NO_THREAD")
        if self.settings.os in ["Linux", "FreeBSD"] and self.options.with_thread:
            self.cpp_info.system_libs.append("pthread")
