from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=2.4"


class SdlttfConan(ConanFile):
    name = "sdl_ttf"
    package_type = "library"
    description = "A TrueType font library for SDL"
    license = "Zlib"
    topics = ("sdl2", "sdl2_ttf", "sdl", "sdl_ttf", "ttf", "font")
    homepage = "https://www.libsdl.org/projects/SDL_ttf"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_harfbuzz": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_harfbuzz": False,
    }

    languages = "C"
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("freetype/2.13.2")
        # https://github.com/conan-io/conan-center-index/pull/18366#issuecomment-1625464996
        self.requires("sdl/2.28.3", transitive_headers=True, transitive_libs=True)
        if self.options.get_safe("with_harfbuzz"):
            self.requires("harfbuzz/[>=8.3.0]")

    def validate(self):
        if Version(self.version).major != Version(self.dependencies["sdl"].ref.version).major:
            raise ConanInvalidConfiguration("sdl & sdl_ttf must have the same major version")

        if self.options.shared != self.dependencies["sdl"].options.shared:
            raise ConanInvalidConfiguration("sdl & sdl_ttf must be built with the same 'shared' option value")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.17]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["SDL2TTF_SAMPLES"] = False
        tc.cache_variables["SDL2TTF_VENDORED"] = False
        tc.cache_variables["SDL2TTF_HARFBUZZ"] = self.options.with_harfbuzz
        tc.cache_variables["SDL2TTF_DEBUG_POSTFIX"] = ""
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "SDL2_ttf.framework"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        suffix = "-static" if not self.options.shared else ""

        self.cpp_info.set_property("cmake_file_name", "SDL2_ttf")
        self.cpp_info.set_property("pkg_config_name", "SDL2_ttf")

        self.cpp_info.components["_sdl2_ttf"].set_property("cmake_target_name",f"SDL2_ttf::SDL2_ttf{suffix}")
        self.cpp_info.components["_sdl2_ttf"].includedirs.append(os.path.join("include", "SDL2"))
        self.cpp_info.components["_sdl2_ttf"].libs = [f"SDL2_ttf"]
        self.cpp_info.components["_sdl2_ttf"].requires = ["freetype::freetype", "sdl::libsdl2"]
        if self.options.get_safe("with_harfbuzz"):
            self.cpp_info.components["_sdl2_ttf"].requires.append("harfbuzz::harfbuzz")
