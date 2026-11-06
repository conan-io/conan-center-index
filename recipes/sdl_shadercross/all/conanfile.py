from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=2.4"


class SDLShadercrossConan(ConanFile):
    name = "sdl_shadercross"
    description = "Shader translation library and tool for SDL's GPU API (built without DXC: no HLSL source input and no DXIL output)"
    topics = ("sdl", "sdl3", "gpu", "shader", "spirv", "msl", "hlsl")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libsdl-org/SDL_shadercross"
    license = "Zlib"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "cli": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "cli": True,
    }
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("sdl/[>=3.2.0 <4]", transitive_headers=True)
        self.requires("spirv-cross/1.4.357.0")

    def validate(self):
        if self.options.shared and not self.dependencies["sdl"].options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} shared requires sdl shared")
        spirv_cross = self.dependencies["spirv-cross"].options
        if not spirv_cross.shared and not (spirv_cross.c_api and spirv_cross.glsl and spirv_cross.hlsl and spirv_cross.msl):
            raise ConanInvalidConfiguration(f"{self.ref} requires spirv-cross with c_api, glsl, hlsl and msl")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.22 <5]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        rmdir(self, os.path.join(self.source_folder, "external"))

    @property
    def _spirv_cross_shared(self):
        return self.dependencies["spirv-cross"].options.shared

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["SDLSHADERCROSS_DXC"] = False
        tc.cache_variables["SDLSHADERCROSS_SHARED"] = self.options.shared
        tc.cache_variables["SDLSHADERCROSS_STATIC"] = not self.options.shared
        tc.cache_variables["SDLSHADERCROSS_SPIRVCROSS_SHARED"] = self._spirv_cross_shared
        tc.cache_variables["SDLSHADERCROSS_VENDORED"] = False
        tc.cache_variables["SDLSHADERCROSS_CLI"] = self.options.cli
        tc.cache_variables["SDLSHADERCROSS_CLI_STATIC"] = False
        tc.cache_variables["SDLSHADERCROSS_TESTS"] = False
        tc.cache_variables["SDLSHADERCROSS_INSTALL"] = True
        tc.cache_variables["SDLSHADERCROSS_INSTALL_CPACK"] = False
        tc.cache_variables["SDLSHADERCROSS_INSTALL_MAN"] = False
        tc.cache_variables["SDLSHADERCROSS_INSTALL_RUNTIME"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.set_property("spirv-cross", "cmake_file_name",
                          "spirv_cross_c_shared" if self._spirv_cross_shared else "spirv_cross_c")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "cmake"))

    def package_info(self):
        lib_postfix = ""
        if self.settings.compiler == "msvc" and not self.options.shared:
            lib_postfix += "-static"

        self.cpp_info.set_property("cmake_file_name", "SDL3_shadercross")
        self.cpp_info.set_property("cmake_target_name", "SDL3_shadercross::SDL3_shadercross")
        alias = "shared" if self.options.shared else "static"
        self.cpp_info.set_property("cmake_target_aliases", [f"SDL3_shadercross::SDL3_shadercross-{alias}"])
        self.cpp_info.set_property("pkg_config_name", "sdl3-shadercross")
        self.cpp_info.libs = [f"SDL3_shadercross{lib_postfix}"]
        spirv_cross = "spirv-cross-c-shared" if self._spirv_cross_shared else "spirv-cross-c"
        self.cpp_info.requires = ["sdl::sdl3", f"spirv-cross::{spirv_cross}"]
