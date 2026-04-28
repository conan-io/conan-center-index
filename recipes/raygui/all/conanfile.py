from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.53.0"


class RayguiConan(ConanFile):
    name = "raygui"
    description = "A simple and easy-to-use immediate-mode gui library."
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/raysan5/raygui"
    topics = ("gui", "raylib", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def requirements(self):
        self.requires("raylib/[>=5 <7]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "raygui.h", src=os.path.join(self.source_folder, "src"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.requires = ["raylib::raylib"]
        self.cpp_info.set_property("cmake_file_name", "raygui")
        self.cpp_info.set_property("cmake_target_name", "raygui::raygui")
        self.cpp_info.set_property("pkg_config_name", "raygui")
