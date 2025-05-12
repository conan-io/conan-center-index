import os

from conan import ConanFile
from conan.tools.layout import basic_layout
from conan.tools.files import copy, get

required_conan_version = ">=1.52.0"


class FireHppConan(ConanFile):
    name = "iconfontcppheaders"
    description = "Headers for icon fonts Font Awesome, Fork Awesome, Google Material Design Icons, Google Material Design Symbols, Pictogrammers Material Design icons, Kenney game icons, Fontaudio, Codicons and Lucide."
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/juliettef/IconFontCppHeaders"
    topics = ("icons", "fonts", "icon-fonts", "header-only")
    no_copy_source = True

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain"

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "licence.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", self.source_folder, os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
