from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir, save
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class SdlttfConan(ConanFile):
    name = "sdl_ttf"
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

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "2.20.0":
            del self.options.with_harfbuzz

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")
        if Version(self.version) >= "2.20.0":
            self.options["sdl"].shared = self.options.shared

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("freetype/2.13.2")
        # https://github.com/conan-io/conan-center-index/pull/18366#issuecomment-1625464996
        self.requires("sdl/2.28.3", transitive_headers=True, transitive_libs=True)
        if self.options.get_safe("with_harfbuzz"):
            self.requires("harfbuzz/8.3.0")

    def validate(self):
        if Version(self.version).major != Version(self.dependencies["sdl"].ref.version).major:
            raise ConanInvalidConfiguration("sdl & sdl_ttf must have the same major version")

        if Version(self.version) >= "2.20.0":
            if self.options.shared != self.dependencies["sdl"].options.shared:
                raise ConanInvalidConfiguration("sdl & sdl_ttf must be built with the same 'shared' option value")
        else:
            if is_msvc(self) and self.options.shared:
                raise ConanInvalidConfiguration(f"{self.ref} shared is not supported with Visual Studio")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) >= "2.20.0":
            tc.variables["SDL2TTF_SAMPLES"] = False
            tc.variables["SDL2TTF_VENDORED"] = False
            tc.variables["SDL2TTF_HARFBUZZ"] = self.options.with_harfbuzz
            tc.variables["SDL2TTF_DEBUG_POSTFIX"] = ""
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        # missing from distribution (only in 2.0.15?)
        save(self, os.path.join(self.source_folder, "SDL2_ttfConfig.cmake"), "")

        # workaround for a side effect of CMAKE_FIND_PACKAGE_PREFER_CONFIG ON in conan toolchain
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "find_package(Freetype REQUIRED)",
                        "find_package(Freetype REQUIRED MODULE)")

    def build(self):
        self._patch_sources()
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
        suffix = "-static" if Version(self.version) >= "2.20.0" and not self.options.shared else ""

        self.cpp_info.set_property("cmake_file_name", "SDL2_ttf")
        self.cpp_info.set_property("pkg_config_name", "SDL2_ttf")

        self.cpp_info.components["_sdl2_ttf"].set_property("cmake_target_name",f"SDL2_ttf::SDL2_ttf{suffix}")
        self.cpp_info.components["_sdl2_ttf"].includedirs.append(os.path.join("include", "SDL2"))
        self.cpp_info.components["_sdl2_ttf"].libs = [f"SDL2_ttf"]
        self.cpp_info.components["_sdl2_ttf"].requires = ["freetype::freetype", "sdl::libsdl2"]
        if self.options.get_safe("with_harfbuzz"):
            self.cpp_info.components["_sdl2_ttf"].requires.append("harfbuzz::harfbuzz")
        if Version(self.version) <= "2.0.18" and is_apple_os(self) and self.options.shared:
            self.cpp_info.components["_sdl2_ttf"].frameworks = [
                "AppKit", "CoreGraphics", "CoreFoundation", "CoreServices"
        ]

        # TODO: to remove in conan v2
        self.cpp_info.names["cmake_find_package"] = "SDL2_ttf"
        self.cpp_info.names["cmake_find_package_multi"] = "SDL2_ttf"
        self.cpp_info.components["_sdl2_ttf"].names["cmake_find_package"] = f"SDL2_ttf{suffix}"
        self.cpp_info.components["_sdl2_ttf"].names["cmake_find_package_multi"] = f"SDL2_ttf{suffix}"
