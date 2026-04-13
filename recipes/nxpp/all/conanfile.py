from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os


class NxppConan(ConanFile):
    name = "nxpp"
    package_type = "header-library"

    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Mik1810/nxpp"
    description = "Header-only C++20 graph library on top of Boost Graph Library"
    topics = ("graph", "boost", "bgl", "header-only", "cxx20")

    settings = "os", "arch", "compiler", "build_type"
    default_options = {"boost/*:header_only": True}
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "20")

    def requirements(self):
        self.requires("boost/1.86.0", transitive_headers=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package_id(self):
        self.info.clear()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=self.package_folder)
        copy(
            self,
            "*.hpp",
            src=os.path.join(self.source_folder, "include"),
            dst=os.path.join(self.package_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.set_property("cmake_file_name", "nxpp")
        self.cpp_info.set_property("cmake_target_name", "nxpp::nxpp")
        self.cpp_info.requires = ["boost::boost"]
