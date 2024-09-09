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
    topics = ("gui", "minimal")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("xorg/system")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "fenster.h", self.source_folder, os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.requires.append("xorg::x11")
            # Also has an optional dependency on "asound" if fenster_audio.h is used.
            # It can be provided either as a system lib or via libalsa Conan package.
            # I'll leave it for the consumer to handle to keep the recipe simple.
        elif is_apple_os(self):
            self.cpp_info.frameworks = ["Cocoa", "AudioToolbox"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["gdi32", "winmm"]
