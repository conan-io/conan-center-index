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
    options = {"with_protected": [True, False]}
    default_options = {"with_protected": False}

    def requirements(self):
        if self.options.with_protected:
            self.requires("libsodium/[~1.0.20]")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 11)
        if str(self.settings.arch) not in ["x86", "x86_64", "armv8"]:
            raise ConanInvalidConfiguration("Not supported architecture. See https://github.com/imakris/mexce#requirements")
        if self.options.with_protected and self.settings.arch == "x86":
            raise ConanInvalidConfiguration("with_protected requires x86_64 or armv8. See https://github.com/imakris/mexce/blob/master/docs/protected_expressions.md")

    def package_id(self):
        self.info.settings.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "mexce.h", self.source_folder,
             os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE*", self.source_folder,
             os.path.join(self.package_folder, "licenses"))
        if self.options.with_protected:
            copy(self, "mexce_protected*.h", self.source_folder,
                 os.path.join(self.package_folder, "include"))
            copy(self, "THIRD_PARTY_NOTICES.md", self.source_folder,
                 os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "mexce")
        self.cpp_info.set_property("cmake_target_name", "mexce::mexce")
        if self.options.with_protected:
            self.cpp_info.set_property("cmake_target_name", "mexce::all")
            self.cpp_info.set_property("pkg_config_name", "mexce-all")
            self.cpp_info.components["mexce"].bindirs = []
            self.cpp_info.components["mexce"].libdirs = []
            self.cpp_info.components["mexce"].set_property("cmake_target_name", "mexce::mexce")
            self.cpp_info.components["mexce"].set_property("pkg_config_name", "mexce")
            self.cpp_info.components["protected"].bindirs = []
            self.cpp_info.components["protected"].libdirs = []
            self.cpp_info.components["protected"].set_property("cmake_target_name", "mexce::protected")
            self.cpp_info.components["protected"].set_property("pkg_config_name", "mexce-protected")
            self.cpp_info.components["protected"].requires = ["mexce", "libsodium::libsodium"]
