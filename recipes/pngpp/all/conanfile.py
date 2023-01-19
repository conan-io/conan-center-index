from conan import ConanFile
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.52.0"


class PngppConan(ConanFile):
    name = "pngpp"
    description = "A C++ wrapper for libpng library."
    license = "BSD-3-Clause"
    topics = ("png++", "png")
    homepage = "https://www.nongnu.org/pngpp"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libpng/1.6.38")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        apply_conandata_patches(self)

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", src=self.source_folder, dst=os.path.join(self.package_folder, "include", "png++"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
