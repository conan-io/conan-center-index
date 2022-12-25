from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir, save
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


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
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("freetype/2.12.1")
        self.requires("sdl/2.26.0")

    def validate(self):
        if is_msvc(self) and self.info.options.shared:
            raise ConanInvalidConfiguration("sdl_ttf shared is not supported with Visual Studio")
        if Version(self.version).major != Version(self.dependencies["sdl"].ref.version).major:
            raise ConanInvalidConfiguration("sdl & sdl_ttf must have the same major version")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
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
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "SDL2_ttf.framework"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SDL2_ttf")
        self.cpp_info.set_property("cmake_target_name", "SDL2_ttf::SDL2_ttf")
        self.cpp_info.set_property("pkg_config_name", "SDL2_ttf")

        self.cpp_info.includedirs.append(os.path.join("include", "SDL2"))
        self.cpp_info.libs = ["SDL2_ttf"]
        self.cpp_info.requires = ["freetype::freetype", "sdl::libsdl2"]

        # TODO: to remove in conan v2
        self.cpp_info.names["cmake_find_package"] = "SDL2_ttf"
        self.cpp_info.names["cmake_find_package_multi"] = "SDL2_ttf"
