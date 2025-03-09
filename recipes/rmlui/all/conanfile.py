import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.files import get, replace_in_file, copy, rmdir
from conan.tools.scm import Version

required_conan_version = ">=2.0"

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
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_rtti_and_exceptions": [True, False],
        "font_interface": ["freetype", None],
        "matrix_mode": ["column_major", "row_major"],
        "with_lua_bindings": [True, False],
        "with_thirdparty_containers": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_rtti_and_exceptions": True,
        "font_interface": "freetype",
        "matrix_mode": "column_major",
        "with_lua_bindings": False,
        "with_thirdparty_containers": True
    }

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
        check_min_cppstd(self, 14)

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
        copy(self, "*LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"), excludes=("Samples/*", "Tests/*"))
        if Version(self.version) < 4:
            copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
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
