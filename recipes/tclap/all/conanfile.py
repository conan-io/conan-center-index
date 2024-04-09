from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
import os


class TclapConan(ConanFile):
    name = "tclap"
    license = "MIT"
    homepage = "https://sourceforge.net/projects/tclap/"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Templatized Command Line Argument Parser"
    topics = ("parser", "command-line", "header-only")
    settings = "os", "compiler", "build_type", "arch"
    package_type = "header-library"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
