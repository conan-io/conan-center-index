from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=2.4"


class SDLImageConan(ConanFile):
    name = "sdl_image"
    description = "SDL_image is an image file loading library"
    topics = ("sdl2", "sdl", "images", "opengl")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.libsdl.org/projects/SDL_image/"
    license = "MIT"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "bmp": [True, False],
        "gif": [True, False],
        "lbm": [True, False],
        "pcx": [True, False],
        "pnm": [True, False],
        "svg": [True, False],
        "tga": [True, False],
        "qoi": [True, False],
        "xcf": [True, False],
        "xpm": [True, False],
        "xv": [True, False],
        "with_libjpeg": [True, False],
        "with_libtiff": [True, False],
        "with_libpng": [True, False],
        "with_libwebp": [True, False],
        "with_avif": [True, False],
        "with_jxl": [True, False],
        "imageio": [True, False],
        "wic": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "bmp": True,
        "gif": True,
        "lbm": True,
        "pcx": True,
        "pnm": True,
        "svg": True,
        "tga": True,
        "qoi": True,
        "xcf": True,
        "xpm": True,
        "xv": True,
        "with_libjpeg": True,
        "with_libtiff": True,
        "with_libpng": True,
        "with_libwebp": True,
        "with_avif": False,
        "with_jxl": False,
        "imageio": False,
        "wic": False,
    }
    implements = ["auto_shared_fpic"]
    languages = "C"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not is_apple_os(self):
            del self.options.imageio
        if self.settings.os != "Windows":
            del self.options.wic

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("sdl/[>=2.32 <3]", transitive_headers=True)
        if self.options.with_libtiff:
            self.requires("libtiff/4.6.0")
        if self.options.with_libjpeg:
            self.requires("libjpeg/[>=9e]")
        if self.options.with_libpng:
            self.requires("libpng/[>=1.6 <2]")
        if self.options.with_libwebp:
            self.requires("libwebp/[>=1.3.2 <2]")
        if self.options.with_avif:
            self.requires("libavif/[>=1.0.1 <2]")
        if self.options.with_jxl:
            self.requires("libjxl/0.11.1")

    def validate(self):
        if self.options.shared and not self.dependencies["sdl"].options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} shared requires sdl shared")
        if Version(self.version).major != Version(self.dependencies["sdl"].ref.version).major:
            raise ConanInvalidConfiguration(f"{self.ref} and sdl must have the same major version")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["SDL2IMAGE_VENDORED"] = False
        tc.cache_variables["SDL2IMAGE_DEPS_SHARED"] = False
        tc.cache_variables["SDL2IMAGE_SAMPLES"] = False
        tc.cache_variables["SDL2IMAGE_AVIF"] = self.options.with_avif
        tc.cache_variables["SDL2IMAGE_BMP"] = self.options.bmp
        tc.cache_variables["SDL2IMAGE_GIF"] = self.options.gif
        tc.cache_variables["SDL2IMAGE_JPG"] = self.options.with_libjpeg
        tc.cache_variables["SDL2IMAGE_JXL"] = self.options.with_jxl
        tc.cache_variables["SDL2IMAGE_LBM"] = self.options.lbm
        tc.cache_variables["SDL2IMAGE_PCX"] = self.options.pcx
        tc.cache_variables["SDL2IMAGE_PNG"] = self.options.with_libpng
        tc.cache_variables["SDL2IMAGE_PNM"] = self.options.pnm
        tc.cache_variables["SDL2IMAGE_QOI"] = self.options.qoi
        tc.cache_variables["SDL2IMAGE_SVG"] = self.options.svg
        tc.cache_variables["SDL2IMAGE_TGA"] = self.options.tga
        tc.cache_variables["SDL2IMAGE_TIF"] = self.options.with_libtiff
        tc.cache_variables["SDL2IMAGE_WEBP"] = self.options.with_libwebp
        tc.cache_variables["SDL2IMAGE_XCF"] = self.options.xcf
        tc.cache_variables["SDL2IMAGE_XPM"] = self.options.xpm
        tc.cache_variables["SDL2IMAGE_XV"] = self.options.xv
        tc.cache_variables["SDL2IMAGE_BACKEND_WIC"] = self.options.get_safe("wic")
        tc.cache_variables["SDL2IMAGE_BACKEND_IMAGEIO"] = self.options.get_safe("imageio")
        tc.generate()
        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        rmdir(self, os.path.join(self.source_folder, "external"))
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "SDL2_image.framework"))
        rmdir(self, os.path.join(self.package_folder, "cmake"))

    def package_info(self):
        lib_postfix = ""
        if self.settings.compiler == "msvc" and not self.options.shared:
            lib_postfix += "-static"
        if self.settings.build_type == "Debug":
            lib_postfix += "d"

        self.cpp_info.set_property("cmake_file_name", "SDL2_image")
        self.cpp_info.set_property("cmake_target_name", "SDL2_image::SDL2_image")
        if not self.options.shared:
            self.cpp_info.set_property("cmake_target_aliases", ["SDL2_image::SDL2_image-static"])
        self.cpp_info.set_property("pkg_config_name", "SDL2_image")
        # TODO: back to global scope in conan v2 once legacy generators removed
        self.cpp_info.components["_sdl_image"].libs = [f"SDL2_image{lib_postfix}"]
        self.cpp_info.components["_sdl_image"].includedirs.append(os.path.join("include", "SDL2"))

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.components["_sdl_image"].set_property("cmake_target_name", "SDL2_image::SDL2_image")
        self.cpp_info.components["_sdl_image"].set_property("pkg_config_name", "SDL2_image")
        self.cpp_info.components["_sdl_image"].requires = ["sdl::sdl"]
        if self.options.with_libtiff:
            self.cpp_info.components["_sdl_image"].requires.append("libtiff::libtiff")
        if self.options.with_libjpeg:
            self.cpp_info.components["_sdl_image"].requires.append("libjpeg::libjpeg")
        if self.options.with_libpng:
            self.cpp_info.components["_sdl_image"].requires.append("libpng::libpng")
        if self.options.with_libwebp:
            self.cpp_info.components["_sdl_image"].requires.append("libwebp::libwebp")
        if self.options.with_avif:
            self.cpp_info.components["_sdl_image"].requires.append("libavif::libavif")
        if self.options.with_jxl:
            self.cpp_info.components["_sdl_image"].requires.append("libjxl::libjxl")
        if self.options.get_safe("imageio") and not self.options.shared:
            self.cpp_info.components["_sdl_image"].frameworks = [
                "CoreFoundation",
                "CoreGraphics",
                "Foundation",
                "ImageIO",
            ]
            if self.settings.os == "Macos":
                self.cpp_info.components["_sdl_image"].frameworks.append("ApplicationServices")
            else:
                self.cpp_info.components["_sdl_image"].frameworks.extend([
                    "MobileCoreServices",
                    "UIKit",
                ])
        if self.options.get_safe("wic"):
            self.cpp_info.system_libs.extend([
                "windowscodecs",
            ])
