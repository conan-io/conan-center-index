from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy, export_conandata_patches, apply_conandata_patches, rmdir
import os


required_conan_version = ">=2.1"


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
        "font_interface": ["freetype", "none"],
        "fPIC": [True, False],
        "matrix_mode": ["column_major", "row_major"],
        "shared": [True, False],
        "with_lua_bindings": [True, False],
    }
    default_options = {
        "font_interface": "freetype",
        "fPIC": True,
        "matrix_mode": "column_major",
        "shared": False,
        "with_lua_bindings": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def validate(self):
        check_min_cppstd(self, 14)

    def requirements(self):
        if self.options.font_interface == "freetype":
            self.requires("freetype/[>=2.13 <3]")

        if self.options.with_lua_bindings:
            self.requires("lua/5.5.0")

        self.requires("robin-hood-hashing/3.11.5", transitive_headers=True)
        self.requires("itlib/1.11.4", transitive_headers=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)
        apply_conandata_patches(self)
        rmdir(self, os.path.join(self.source_folder, "Include", "RmlUi", "Core", "Containers"))

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["RMLUI_LUA_BINDINGS"] = self.options.with_lua_bindings
        tc.cache_variables["RMLUI_SAMPLES"] = False
        tc.cache_variables["RMLUI_CUSTOM_RTTI"] = False
        tc.cache_variables["RMLUI_PRECOMPILED_HEADERS"] = True
        tc.cache_variables["RMLUI_TRACY_PROFILING"] = False
        tc.cache_variables["RMLUI_THIRDPARTY_CONTAINERS"] = True
        tc.cache_variables["RMLUI_MATRIX_ROW_MAJOR"] = self.options.matrix_mode == "row_major"
        tc.cache_variables["RMLUI_FONT_ENGINE"] = str(self.options.font_interface)
        if self.settings.os == "Windows":
            tc.cache_variables["RMLUI_INSTALL_RUNTIME_DEPENDENCIES"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("lua", "cmake_target_name", "Lua::Lua")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(
            self,
            "LICENSE.txt",
            src=os.path.join(self.source_folder, "Source", "Debugger"),
            dst=os.path.join(self.package_folder, "licenses", "Source", "Debugger"),
        )
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "RmlUi")
        self.cpp_info.set_property("cmake_target_name", "RmlUi::RmlUi")

        # Core component
        core = self.cpp_info.components["core"]
        core.libs = ["rmlui"]
        core.set_property("cmake_target_name", "RmlUi::Core")
        core.requires = ["robin-hood-hashing::robin-hood-hashing", "itlib::itlib"]
        if self.options.font_interface == "freetype":
            core.requires.append("freetype::freetype")
        if self.options.matrix_mode == "row_major":
            core.defines.append("RMLUI_MATRIX_ROW_MAJOR")
        if not self.options.shared:
            core.defines.append("RMLUI_STATIC_LIB")

        # Lua component
        if self.options.with_lua_bindings:
            self.cpp_info.components["rmlui_lua"].libs = ["rmlui_lua"]
            self.cpp_info.components["rmlui_lua"].set_property("cmake_target_name", "RmlUi::Lua")
            self.cpp_info.components["rmlui_lua"].requires = ["core", "lua::lua"]

        # Debugger component
        self.cpp_info.components["rmlui_debugger"].libs = ["rmlui_debugger"]
        self.cpp_info.components["rmlui_debugger"].set_property("cmake_target_name", "RmlUi::Debugger")
        self.cpp_info.components["rmlui_debugger"].requires = ["core"]
