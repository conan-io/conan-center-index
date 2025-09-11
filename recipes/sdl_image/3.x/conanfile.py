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
    homepage = "https://github.com/libsdl-org/SDL_image"
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
        # Headers are exposed https://github.com/conan-io/conan-center-index/pull/16167#issuecomment-1508347351
        self.requires("sdl/[>=3.2.20 <4]", transitive_headers=True)
        if self.options.with_libtiff:
            self.requires("libtiff/4.6.0")
        if self.options.with_libjpeg:
            self.requires("libjpeg/[>=9e]")
        if self.options.with_libpng:
            self.requires("libpng/[>=1.6 <2]")
        if self.options.with_libwebp:
            self.requires("libwebp/[>=1.3.2 <2]")
        if self.options.get_safe("with_avif"):
            self.requires("libjxl/0.11.1")
            self.requires("libavif/[>=1.0.1 <2]")


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
        tc.cache_variables["SDLIMAGE_VENDORED"] = False
        tc.cache_variables["SDLIMAGE_DEPS_SHARED"] = False
        tc.cache_variables["SDLIMAGE_SAMPLES"] = False
        tc.cache_variables["SDLIMAGE_AVIF"] = self.options.get_safe("with_avif")
        tc.cache_variables["SDLIMAGE_BMP"] = self.options.bmp
        tc.cache_variables["SDLIMAGE_GIF"] = self.options.gif
        tc.cache_variables["SDLIMAGE_JPG"] = self.options.with_libjpeg
        tc.cache_variables["SDLIMAGE_JXL"] = self.options.get_safe("with_jxl")
        tc.cache_variables["SDLIMAGE_LBM"] = self.options.lbm
        tc.cache_variables["SDLIMAGE_PCX"] = self.options.pcx
        tc.cache_variables["SDLIMAGE_PNG"] = self.options.with_libpng
        tc.cache_variables["SDLIMAGE_PNM"] = self.options.pnm
        tc.cache_variables["SDLIMAGE_QOI"] = self.options.get_safe("qoi")
        tc.cache_variables["SDLIMAGE_SVG"] = self.options.svg
        tc.cache_variables["SDLIMAGE_TGA"] = self.options.tga
        tc.cache_variables["SDLIMAGE_TIF"] = self.options.with_libtiff
        tc.cache_variables["SDLIMAGE_WEBP"] = self.options.with_libwebp
        tc.cache_variables["SDLIMAGE_XCF"] = self.options.xcf
        tc.cache_variables["SDLIMAGE_XPM"] = self.options.xpm
        tc.cache_variables["SDLIMAGE_XV"] = self.options.xv
        tc.cache_variables["SDLIMAGE_BACKEND_WIC"] = self.options.get_safe("wic")
        tc.cache_variables["SDLIMAGE_BACKEND_IMAGEIO"] = self.options.get_safe("imageio")
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
        rmdir(self, os.path.join(self.package_folder, "cmake"))

    def package_info(self):
        lib_postfix = ""
        if self.settings.compiler == "msvc" and not self.options.shared:
            lib_postfix += "-static"

        self.cpp_info.set_property("cmake_file_name", "SDL3_image")
        self.cpp_info.set_property("cmake_target_name", "SDL3_image::SDL3_image")
        if not self.options.shared:
            self.cpp_info.set_property("cmake_target_aliases", ["SDL3_image::SDL3_image-static"])
        self.cpp_info.libs = [f"SDL3_image{lib_postfix}"]

        if self.options.get_safe("imageio") and not self.options.shared:
            # IMG_ImageIO.m: https://github.com/libsdl-org/SDL_image/blob/release-3.2.4/src/IMG_ImageIO.m#L17-L26
            # Need for CoreGraphics: https://discourse.libsdl.org/t/sdl-image-issue-470-add-coregraphics-imageio-and-mobilecoreservices-required-from-img-imageio-mm-for-ios-specific-builds-e2923/59516
            if self.settings.os == "Macos":
                self.cpp_info.frameworks = ["ApplicationServices", "Foundation"]
            else:
                self.cpp_info.frameworks = ["CoreGraphics", "ImageIO", "MobileCoreServices", "UIKit", "Foundation"]
        if self.options.get_safe("wic"):
            self.cpp_info.system_libs.extend(["windowscodecs"])
