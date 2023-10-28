import os

from conan import ConanFile
from conan.tools.cmake import cmake_layout
from conan.tools.files import copy, get

required_conan_version = ">=1.52.0"


class FireHppConan(ConanFile):
    name = "iconfontcppheaders"
    description = "Headers for icon fonts Font Awesome, Fork Awesome, Google Material Design, Kenney game icons, Fontaudio, Codicons, Pictogrammers Material Design icons."
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/juliettef/IconFontCppHeaders"
    topics = ("icons", "fonts", "icon-fonts", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain"

    def layout(self):
        cmake_layout(self, src_folder='src')

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "licence.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", self.source_folder, os.path.join(self.package_folder, "include", "IconFontCppHeaders"))

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
