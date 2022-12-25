from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class XbyakConan(ConanFile):
    name = "xbyak"
    description = "Xbyak is a C++ header library that enables dynamically to " \
                  "assemble x86(IA32), x64(AMD64, x86-64) mnemonic."
    license = "BSD-3-Clause"
    topics = ("xbyak", "jit", "assembler")
    homepage = "https://github.com/herumi/xbyak"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def package_id(self):
        self.info.clear()

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "COPYRIGHT", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", src=os.path.join(self.source_folder, "xbyak"), dst=os.path.join(self.package_folder, "include", "xbyak"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "xbyak")
        self.cpp_info.set_property("cmake_target_name", "xbyak::xbyak")
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
