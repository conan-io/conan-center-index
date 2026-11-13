import os
from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class LuaBridge3Conan(ConanFile):
    name = "luabridge3"
    description = "A lightweight, dependency-free library for binding Lua to C++"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/kunitoki/LuaBridge3"
    topics = ("lua", "bindings", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE*", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", os.path.join(self.source_folder, "Source", "LuaBridge"),
             os.path.join(self.package_folder, "include", "LuaBridge"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "LuaBridge")
        self.cpp_info.set_property("cmake_target_name", "LuaBridge::LuaBridge")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
