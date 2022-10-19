from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout

import os

required_conan_version = ">=1.52.0"

class LuauConan(ConanFile):
    name = "luau"
    description = "A fast, small, safe, gradually typed embeddable scripting language derived from Lua"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://luau-lang.org/"
    topics = ("lua", "scripting", "typed", "embed")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [False, True],
        "fPIC": [True, False],
        "with_cli": [True, False],
        "with_web": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_cli": False,
        "with_web": False,
    }

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12",
        }

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)
        check_min_vs(self, 191)
        minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
        if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._minimum_cpp_standard}, which your compiler does not support."
            )

        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} does not support shared build in MSVC")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LUAU_BUILD_CLI"] = self.options.with_cli
        tc.variables["LUAU_BUILD_TESTS"] = False
        tc.variables["LUAU_BUILD_WEB"] = self.options.with_web
        tc.variables["LUAU_WERROR"] = False
        tc.variables["LUAU_STATIC_CRT"] = False
        tc.variables["LUAU_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if Version(self.version) >= "0.548" and self.options.shared:
            replace_in_file(self, os.path.join(self.source_folder, "VM", "include", "luaconf.h"),
                "#define LUAI_FUNC __attribute__((visibility(\"hidden\"))) extern",
                "#define LUAI_FUNC extern")

    def build(self):
        self._patch_sources()
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

        self.cpp_info.filenames["cmake_find_package"] = "Luau"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Luau"
        self.cpp_info.names["cmake_find_package_multi"] = "Luau"
        self.cpp_info.names["cmake_find_package"] = "Luau"

        self.cpp_info.components["Ast"].libs = ["Luau.Ast"]
        self.cpp_info.components["Ast"].set_property("cmake_target_name", "Luau::Ast")

        self.cpp_info.components["VM"].libs = ["Luau.VM"]
        self.cpp_info.components["VM"].set_property("cmake_target_name", "Luau::VM")
        self.cpp_info.components["VM"].requires = ["Ast"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["VM"].system_libs = ["m"]

        self.cpp_info.components["Analysis"].libs = ["Luau.Analysis"]
        self.cpp_info.components["Analysis"].set_property("cmake_target_name", "Luau::Analysis")
        self.cpp_info.components["Analysis"].requires = ["Ast"]

        self.cpp_info.components["Compiler"].libs = ["Luau.Compiler"]
        self.cpp_info.components["Compiler"].set_property("cmake_target_name", "Luau::Compiler")
        self.cpp_info.components["Compiler"].requires = ["Ast"]

        self.cpp_info.components["CodeGen"].libs = ["Luau.CodeGen"]
        self.cpp_info.components["CodeGen"].set_property("cmake_target_name", "Luau::CodeGen")
        self.cpp_info.components["CodeGen"].requires = ["Ast"]
        if Version(self.version) >= "0.548":
            self.cpp_info.components["CodeGen"].requires.append("VM")

        if self.options.with_cli:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info(f"Appending PATH environment variable: {bin_path}")
            self.env_info.PATH.append(bin_path)

        if self.options.with_web:
            self.cpp_info.components["Web"].libs = ["Luau.Web"]
            self.cpp_info.components["Web"].set_property("cmake_target_name", "Luau::Web")
            self.cpp_info.components["Web"].requires = ["Compiler", "VM"]
