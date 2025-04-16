from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir, save
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=2"


class SdlttfConan(ConanFile):
    name = "sdl_ttf"
    description = "A TrueType font library for SDL"
    license = "Zlib"
    topics = ("sdl3", "sdl3_ttf", "sdl", "ttf", "font")
    homepage = "https://www.libsdl.org/projects/SDL_ttf"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_harfbuzz": [True, False],
        "with_plutosvg": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "with_harfbuzz": True,
        "with_plutosvg": True,
    }

    implements = ["auto_shared_fpic"]
    languages = "C"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("freetype/2.13.2")
        # https://github.com/conan-io/conan-center-index/pull/18366#issuecomment-1625464996
        self.requires("sdl/3.2.6", transitive_headers=True, transitive_libs=True)
        if self.options.with_harfbuzz:
            self.requires("harfbuzz/8.3.0")
        if self.options.with_plutosvg:
            self.requires("plutosvg/0.0.6")

    def validate(self):
        if Version(self.version).major != Version(self.dependencies["sdl"].ref.version).major:
            raise ConanInvalidConfiguration("sdl & sdl_ttf must have the same major version")

        if self.options.shared:
            raise ConanInvalidConfiguration("This recipe does not support shared libraries for now, contributions welcome")

        if self.options.shared != self.dependencies["sdl"].options.shared:
            raise ConanInvalidConfiguration("sdl & sdl_ttf must be built with the same 'shared' option value")


    def build_requirements(self):
        self.tool_requires("cmake/[>=3.17 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["SDLTTF_VENDORED"] = False
        tc.cache_variables["SDLTTF_STRICT"] = True
        tc.cache_variables["SDLTTF_SAMPLES"] = False
        tc.cache_variables["SDLTTF_HARFBUZZ"] = self.options.with_harfbuzz
        tc.cache_variables["SDLTTF_PLUTOSVG"] = self.options.with_plutosvg

        tc.generate()
        deps = CMakeDeps(self)
        deps.set_property("freetype", "cmake_file_name", "Freetype")
        deps.set_property("freetype", "cmake_target_name", "Freetype::Freetype")
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
        # rmdir(self, os.path.join(self.package_folder, "cmake"))
        # rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        # rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        # rmdir(self, os.path.join(self.package_folder, "SDL2_ttf.framework"))
        # rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["SDL3_ttf"]
        self.cpp_info.set_property("cmake_file_name", "SDL3_ttf")

        suffix = "-static" if not self.options.shared else ""
        self.cpp_info.set_property("cmake_target_name", f"SDL3_ttf::SDL3_ttf{suffix}")

