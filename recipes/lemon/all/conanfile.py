from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, load, save
import os

required_conan_version = ">=1.53.0"


class LemonConan(ConanFile):
    name = "lemon"
    description = "The Lemon program reads a grammar of the input language and emits C-code to implement a parser for that language."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sqlite.org/lemon.html"
    topics = ("grammar", "lexer", "lalr", "parser", "generator", "sqlite")
    license = "Unlicense"
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)
        export_conandata_patches(self)

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LEMON_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def _extract_license_text(self):
        header = load(self, os.path.join(self.source_folder, "tool", "lempar.c"))
        return "\n".join(line.strip(" \n*") for line in header[3:header.find("*******", 1)].splitlines())

    def package(self):
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._extract_license_text())
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
