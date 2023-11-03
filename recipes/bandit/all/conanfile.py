from conan import ConanFile
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.52.0"


class BanditConan(ConanFile):
    name = "bandit"
    description = "Human-friendly unit testing for C++11"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/banditcpp/bandit"
    topics = ("testing", "header-only")
    package_type = "header-library"

    def export_sources(self):
        export_conandata_patches(self)

    def requirements(self):
        self.requires("snowhouse/5.0.0", transitive_headers=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        basic_layout(self, src_folder="src")

    def build(self):
        apply_conandata_patches(self)

    def package(self):
        copy(self, "LICENSE.txt", src=os.path.join(self.source_folder, "docs"), dst=os.path.join(self.package_folder, "licenses"))
        copy(self,
             pattern="*.h",
             dst=os.path.join(self.package_folder, "include", "bandit"),
             src=os.path.join(self.source_folder, "bandit"))

    def package_id(self):
        self.info.clear()

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
