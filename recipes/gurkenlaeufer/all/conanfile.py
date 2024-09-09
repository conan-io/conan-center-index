from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, rmdir
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=1.52.0"


class GurkenlaeuferConan(ConanFile):
    name = "gurkenlaeufer"
    description = "Simple way to write cucumber tests for your C++ projects"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/paulelsner/gurkenlaeufer"
    topics = ("testing", "header-only", "cucumber", "gherkin")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 11

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("gtest/1.12.1", transitive_headers=True)

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        rmdir(self, os.path.join(self.source_folder, "gtest"))

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder,"licenses"))
        copy(self, "*.h", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))

    def package_info(self):
        # Folders not used for header-only
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
