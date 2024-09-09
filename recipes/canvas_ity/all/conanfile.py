from conan import ConanFile
from conan.tools.files import get, copy, load, save
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=1.50.0"


class CanvasItyConan(ConanFile):
    name = "canvas_ity"
    description = "A tiny, single-header <canvas>-like 2D rasterizer for C++"
    license = "ISC"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/a-e-k/canvas_ity"
    topics = ("rasterizer", "canvas", "2d", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        filename = os.path.join(self.source_folder, "src", "canvas_ity.hpp")
        file_content = load(self, filename)
        license_end = "// ======== ABOUT ========"
        license_contents = file_content[:file_content.find(license_end)].replace("//", "")
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_contents)

        copy(
            self,
            pattern="*.hpp",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "src"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
