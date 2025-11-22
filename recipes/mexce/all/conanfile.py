from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os


class MexceConan(ConanFile):
    name = "mexce"
    license = "BSD-2-Clause"
    homepage = "https://github.com/imakris/mexce"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Single-header, dependency-free JIT compiler for scalar mathematical expressions."
    topics = ("jit", "math", "expression-parser", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 11)
        if str(self.settings.arch) not in ("x86", "x86_64"):
            raise ConanInvalidConfiguration("mexce only supports x86 and x86_64 architectures")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "mexce.h", self.source_folder,
             os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE*", self.source_folder,
             os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "mexce")
        self.cpp_info.set_property("cmake_target_name", "mexce::mexce")
