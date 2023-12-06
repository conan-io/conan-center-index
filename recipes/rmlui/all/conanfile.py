from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, replace_in_file, copy, rmdir
from conan.tools.scm import Version
import os


required_conan_version = ">=1.53.0"

class RmluiConan(ConanFile):
    name = "rmlui"
    description = "RmlUi - The HTML/CSS User Interface Library Evolved"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mikke89/RmlUi"
    topics = ("css", "gui", "html", "lua", "rmlui")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "enable_rtti_and_exceptions": [True, False],
        "font_interface": ["freetype", None],
        "fPIC": [True, False],
        "matrix_mode": ["column_major", "row_major"],
        "shared": [True, False],
        "with_lua_bindings": [True, False],
        "with_thirdparty_containers": [True, False]
    }
    default_options = {
        "enable_rtti_and_exceptions": True,
        "font_interface": "freetype",
        "fPIC": True,
        "matrix_mode": "column_major",
        "shared": False,
        "with_lua_bindings": False,
        "with_thirdparty_containers": True
    }

    @property
    def _minimum_compilers_version(self):
        # Reference: https://en.cppreference.com/w/cpp/compiler_support/14
        return {
            "apple-clang": "5.1",
            "clang": "3.4",
            "gcc": "5",
            "intel": "17",
            "sun-cc": "5.15",
            "Visual Studio": "15"
        }

    @property
    def _minimum_cpp_standard(self):
        return 14

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < 4:
            del self.options.matrix_mode

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)

        def loose_lt_semver(v1, v2):
            return all(int(p1) < int(p2) for p1, p2 in zip(str(v1).split("."), str(v2).split(".")))

        min_version = self._minimum_compilers_version.get(
            str(self.settings.compiler))
        if not min_version:
            self.output.warning(f"{self.ref} recipe lacks information about the {self.settings.compiler} compiler support.")
        else:
            if loose_lt_semver(str(self.settings.compiler.version), min_version):
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._minimum_cpp_standard} support. "
                    f"The current compiler {self.settings.compiler} {self.settings.compiler.version} does not support it."
                )

    def requirements(self):
        if self.options.font_interface == "freetype":
            self.requires("freetype/2.13.2")

        if self.options.with_lua_bindings:
            self.requires("lua/5.4.6")

        if self.options.with_thirdparty_containers:
            self.requires("robin-hood-hashing/3.11.5", transitive_headers=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_LUA_BINDINGS"] = self.options.with_lua_bindings
        tc.cache_variables["BUILD_SAMPLES"] = False
        tc.cache_variables["DISABLE_RTTI_AND_EXCEPTIONS"] = not self.options.enable_rtti_and_exceptions
        tc.cache_variables["ENABLE_PRECOMPILED_HEADERS"] = True
        tc.cache_variables["ENABLE_TRACY_PROFILING"] = False
        if Version(self.version) >= 4:
            tc.cache_variables["MATRIX_ROW_MAJOR"] = self.options.matrix_mode == "row_major"
        tc.cache_variables["NO_FONT_INTERFACE_DEFAULT"] = not self.options.font_interface
        tc.cache_variables["NO_THIRDPARTY_CONTAINERS"] = not self.options.with_thirdparty_containers
        tc.variables["LIBRARY_VISIBILITY"] = "PUBLIC" if Version(self.version) >= 4 else ""
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        # If we are using robin_hood hashing provided by conan, we need to change its include path
        if self.options.with_thirdparty_containers:
            if Version(self.version) >= 4:
                config_path = os.path.join(self.source_folder, "Include", "RmlUi", "Config", "Config.h")
                replace_in_file(self, config_path, '"../Core/Containers/robin_hood.h"', "<robin_hood.h>")
            else:
                types_h = os.path.join(self.source_folder, "Include", "RmlUi", "Core", "Types.h")
                replace_in_file(self, types_h, '"Containers/robin_hood.h"', "<robin_hood.h>")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=self.source_path.parent)
        cmake.build()

    def package(self):
        copy(self, pattern="*LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder, excludes=("Samples/*", "Tests/*"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "RmlUi"))

    def package_info(self):
        if Version(self.version) >= 4 and self.options.matrix_mode == "row_major":
            self.cpp_info.defines.append("RMLUI_MATRIX_ROW_MAJOR")

        if not self.options.shared:
            self.cpp_info.defines.append("RMLUI_STATIC_LIB")

        if not self.options.with_thirdparty_containers:
            self.cpp_info.defines.append("RMLUI_NO_THIRDPARTY_CONTAINERS")

        self.cpp_info.libs.append("RmlCore")
        self.cpp_info.libs.append("RmlDebugger")

        if Version(self.version) >= 4:
            if self.options.with_lua_bindings:
                self.cpp_info.libs.append("RmlLua")
        else:
            self.cpp_info.libs.append("RmlControls")
            if self.options.with_lua_bindings:
                self.cpp_info.libs.append("RmlCoreLua")
                self.cpp_info.libs.append("RmlControlsLua")
