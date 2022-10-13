from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class NuklearConan(ConanFile):
    name = "nuklear"
    description = "A single-header ANSI C immediate mode cross-platform GUI library."
    license = ["MIT", "Unlicense"]
    topics = ("nuklear", "gui", "header-only")
    homepage = "https://github.com/Immediate-Mode-UI/Nuklear"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def package_id(self):
        self.info.clear()

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=os.path.join(self.source_folder, "src"), dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "nuklear.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
