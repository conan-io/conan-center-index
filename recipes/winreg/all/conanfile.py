from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class WinregConan(ConanFile):
    name = "winreg"
    homepage = "https://github.com/GiovanniDicanio/WinReg"
    description = "Convenient high-level C++ wrapper around the Windows Registry API."
    topics = "registry", "header-only"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _minimum_cpp_standard(self):
        return 17

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("WinReg is only supported on Windows")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        pass

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", os.path.join(self.source_folder, "WinReg"), os.path.join(self.package_folder, "include/WinReg"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
