from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.50.0"


class XbyakConan(ConanFile):
    name = "xbyak"
    description = "Xbyak is a C++ header library that enables dynamically to " \
                  "assemble x86(IA32), x64(AMD64, x86-64) mnemonic."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/herumi/xbyak"
    topics = ("jit", "assembler", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.arch not in ("x86", "x86_64"):
            raise ConanInvalidConfiguration(f"{self.ref} is only available for x86 and x86_64 architecture")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "COPYRIGHT", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", src=os.path.join(self.source_folder, "xbyak"), dst=os.path.join(self.package_folder, "include", "xbyak"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "xbyak")
        self.cpp_info.set_property("cmake_target_name", "xbyak::xbyak")

        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
