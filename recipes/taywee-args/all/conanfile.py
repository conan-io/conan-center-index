from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class TayweeArgsConan(ConanFile):
    name = "taywee-args"
    description = "A simple, small, flexible, single-header C++11 argument parsing library"
    topics = ("args", "argument-parser", "header-only")
    license = "MIT"
    homepage = "https://github.com/Taywee/args"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "args.hxx", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "args")
        self.cpp_info.set_property("cmake_target_name", "taywee::args")
        self.cpp_info.set_property("pkg_config_name", "args")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2
        self.cpp_info.filenames["cmake_find_package"] = "args"
        self.cpp_info.filenames["cmake_find_package_multi"] = "args"
        self.cpp_info.names["cmake_find_package"] = "taywee"
        self.cpp_info.names["cmake_find_package_multi"] = "taywee"
        self.cpp_info.components["libargs"].names["cmake_find_package"] = "args"
        self.cpp_info.components["libargs"].names["cmake_find_package_multi"] = "args"
        self.cpp_info.components["libargs"].set_property("cmake_target_name", "taywee::args")
        self.cpp_info.components["libargs"].set_property("pkg_config_name", "args")
        self.cpp_info.components["libargs"].bindirs = []
        self.cpp_info.components["libargs"].libdirs = []
