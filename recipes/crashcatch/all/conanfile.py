from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=2.1"


class CrashCatchConan(ConanFile):
    name = "crashcatch"
    description = "A cross-platform, single-header C++ crash-reporting library for modern C++ applications."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/keithpotz/CrashCatch"
    topics = ("crash-reporting", "crash-handler", "minidump", "header-only", "single-header")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self,
            **self.conan_data["sources"][self.version],
            strip_root=True)

    def package_id(self):
        # Header-only: binary is the same regardless of compiler/settings
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 17)

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp",
             src=os.path.join(self.source_folder, "include"),
             dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CrashCatch")
        self.cpp_info.set_property("cmake_target_name", "CrashCatch::CrashCatch")

        # No compiled lib — only headers
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["DbgHelp", "User32"]
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
