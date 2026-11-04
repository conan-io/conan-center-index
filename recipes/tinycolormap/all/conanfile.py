import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class TinycolormapConan(ConanFile):
    name = "tinycolormap"
    description = "A header-only, single-file library for colormaps written in C++11"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/yuki-koyama/tinycolormap"
    topics = ("color", "colormap", "visualization", "header-only")
    package_type = "header-library"

    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    options = {
        "with_eigen": [True, False],
        "with_qt": [True, False],
    }
    default_options = {
        "with_eigen": False,
        "with_qt": False,
    }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def requirements(self):
        if self.options.with_eigen:
            self.requires("eigen/3.4.0")
        if self.options.with_qt:
            # Only Qt5 is supported
            self.requires("qt/5.15.13")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        if self.options.with_eigen:
            self.cpp_info.defines.append("TINYCOLORMAP_WITH_EIGEN")
            self.cpp_info.requires.append("eigen::eigen")
        if self.options.with_qt:
            self.cpp_info.defines.append("TINYCOLORMAP_WITH_QT5")
            self.cpp_info.requires.append("qt::qtGui")
