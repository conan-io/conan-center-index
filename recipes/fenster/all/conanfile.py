import os

from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.files import copy, export_conandata_patches, get
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class FensterConan(ConanFile):
    name = "fenster"
    description = "The most minimal cross-platform GUI library"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/zserge/fenster"
    topics = ("gui", "audio", "minimal")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    options = {
        "enable_graphics": [True, False],
        "enable_audio": [True, False],
    }
    default_options = {
        "enable_graphics": True,
        "enable_audio": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            if self.options.enable_graphics:
                self.requires("xorg/system")
            if self.options.enable_audio:
                self.requires("libalsa/1.2.12")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", self.source_folder, os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        if self.options.enable_graphics:
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.requires.append("xorg::x11")
            elif is_apple_os(self):
                self.cpp_info.frameworks.append("Cocoa")
            elif self.settings.os == "Windows":
                self.cpp_info.system_libs.append("gdi32")

        if self.options.enable_audio:
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.requires.append("libalsa::libalsa")
            elif is_apple_os(self):
                self.cpp_info.frameworks.append("AudioToolbox")
            elif self.settings.os == "Windows":
                self.cpp_info.system_libs.append("winmm")
