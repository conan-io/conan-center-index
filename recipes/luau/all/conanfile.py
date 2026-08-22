from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout

import os

required_conan_version = ">=2"

class LuauConan(ConanFile):
    name = "luau"
    description = "A fast, small, safe, gradually typed embeddable scripting language derived from Lua"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://luau-lang.org/"
    topics = ("lua", "scripting", "typed", "embed")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_cli": [True, False],
        "with_web": [True, False],
        "native_code_gen": [True, False],
    }
    default_options = {
        "with_cli": False,
        "with_web": False,
        "native_code_gen": False,
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LUAU_BUILD_CLI"] = self.options.with_cli
        tc.variables["LUAU_BUILD_TESTS"] = False
        tc.variables["LUAU_BUILD_WEB"] = self.options.with_web
        tc.variables["LUAU_WERROR"] = False
        tc.variables["LUAU_STATIC_CRT"] = False
        tc.variables["LUAU_NATIVE"] = self.options.native_code_gen
        tc.variables["LUAU_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "lua_LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Luau")
        self.cpp_info.set_property("cmake_target_name", "Luau::Luau")
        # Common
        self.cpp_info.components["Common"].libs = ["Luau.Common"]
        self.cpp_info.components["Common"].set_property("cmake_target_name", "Luau::Common")
        # Ast
        self.cpp_info.components["Ast"].libs = ["Luau.Ast"]
        self.cpp_info.components["Ast"].set_property("cmake_target_name", "Luau::Ast")
        self.cpp_info.components["Ast"].requires = ["Common"]
        # VM
        self.cpp_info.components["VM"].libs = ["Luau.VM"]
        self.cpp_info.components["VM"].set_property("cmake_target_name", "Luau::VM")
        self.cpp_info.components["VM"].requires = ["Common"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["VM"].system_libs = ["m"]
        # Analysis
        self.cpp_info.components["Analysis"].libs = ["Luau.Analysis"]
        self.cpp_info.components["Analysis"].set_property("cmake_target_name", "Luau::Analysis")
        self.cpp_info.components["Analysis"].requires = ["Ast", "Config", "Compiler", "VM"]
        # Config
        self.cpp_info.components["Config"].libs = ["Luau.Config"]
        self.cpp_info.components["Config"].set_property("cmake_target_name", "Luau::Config")
        self.cpp_info.components["Config"].requires = ["Ast", "Compiler", "VM"]
        # Compiler
        self.cpp_info.components["Compiler"].libs = ["Luau.Compiler"]
        self.cpp_info.components["Compiler"].set_property("cmake_target_name", "Luau::Compiler")
        self.cpp_info.components["Compiler"].requires = ["Ast"]
        # CodeGen
        self.cpp_info.components["CodeGen"].libs = ["Luau.CodeGen"]
        self.cpp_info.components["CodeGen"].set_property("cmake_target_name", "Luau::CodeGen")
        self.cpp_info.components["CodeGen"].requires = ["VM", "Common"]
        # Require
        self.cpp_info.components["Require"].libs = ["Luau.Require"]
        self.cpp_info.components["Require"].set_property("cmake_target_name", "Luau::Require")
        self.cpp_info.components["Require"].requires = ["Config", "VM"]
        # Web
        if self.options.with_web:
            self.cpp_info.components["Web"].libs = ["Luau.Web"]
            self.cpp_info.components["Web"].set_property("cmake_target_name", "Luau::Web")
            self.cpp_info.components["Web"].requires = ["Compiler", "VM", "Analysis"]

