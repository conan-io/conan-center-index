from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class NanosvgConan(ConanFile):
    name = "nanosvg"
    description = "NanoSVG is a simple stupid single-header-file SVG parser."
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/memononen/nanosvg"
    topics = ("nanosvg", "svg", "parser", "header-only")
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
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", src=os.path.join(self.source_folder, "src"), dst=os.path.join(self.package_folder, "include", "nanosvg"))

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "nanosvg"))
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
