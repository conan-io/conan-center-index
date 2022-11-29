from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=1.53.0"


class SDLImageConan(ConanFile):
    name = "sdl_image"
    description = "SDL_image is an image file loading library"
    topics = ("sdl_image", "sdl_image", "sdl2", "sdl", "images", "opengl")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.libsdl.org/projects/SDL_image/"
    license = "MIT"

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
        "xcf": [True, False],
        "xpm": [True, False],
        "xv": [True, False],
        "with_libjpeg": [True, False],
        "with_libjpeg_dynamic_load": [True, False],
        "with_libtiff": [True, False],
        "with_libtiff_dynamic_load": [True, False],
        "with_libpng": [True, False],
        "with_libpng_dynamic_load": [True, False],
        "with_libwebp": [True, False],
        "with_libwebp_dynamic_load": [True, False],
        "imageio": [True, False],
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
        "xcf": True,
        "xpm": True,
        "xv": True,
        "with_libjpeg": True,
        "with_libjpeg_dynamic_load": False,
        "with_libtiff": True,
        "with_libtiff_dynamic_load": False,
        "with_libpng": True,
        "with_libpng_dynamic_load": False,
        "with_libwebp": True,
        "with_libwebp_dynamic_load": False,
        "imageio": False,
    }

    exports_sources = "CMakeLists.txt"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not is_apple_os(self):
            del self.options.imageio

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")
        if not self.options.with_libjpeg:
            del self.options.with_libjpeg_dynamic_load
        if not self.options.with_libtiff:
            del self.options.with_libtiff_dynamic_load
        if not self.options.with_libpng:
            del self.options.with_libpng_dynamic_load
        if not self.options.with_libwebp:
            del self.options.with_libwebp_dynamic_load
        if self.options.shared:
            # sdl static into sdl_image shared is not allowed
            self.options["sdl"].shared = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("sdl/2.26.0")
        if self.options.with_libtiff:
            self.requires("libtiff/4.4.0")
        if self.options.with_libjpeg:
            self.requires("libjpeg/9e")
        if self.options.with_libpng:
            self.requires("libpng/1.6.39")
        if self.options.with_libwebp:
            self.requires("libwebp/1.2.4")

    def validate(self):
        if self.info.options.shared and not self.dependencies["sdl"].options.shared:
            raise ConanInvalidConfiguration("sdl_image shared requires sdl shared")
        if self.info.options.get_safe("with_libjpeg_dynamic_load") and self.dependencies["libjpeg"].options.shared:
            raise ConanInvalidConfiguration("with_libjpeg_dynamic_load=True requires libjpeg:shared=True")
        if self.info.options.get_safe("with_libtiff_dynamic_load") and self.dependencies["libtiff"].options.shared:
            raise ConanInvalidConfiguration("with_libtiff_dynamic_load requires libtiff:shared=True")
        if self.info.options.get_safe("with_libpng_dynamic_load") and self.dependencies["libpng"].options.shared:
            raise ConanInvalidConfiguration("with_libpng_dynamic_load requires libpng:shared=True")
        if self.info.options.get_safe("with_libwebp_dynamic_load") and self.dependencies["libwebp"].options.shared:
            raise ConanInvalidConfiguration("with_libwebp_dynamic_load requires libwebp:shared=True")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SDL_IMAGE_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["SDL2IMAGE_BMP"] = self.options.bmp
        tc.variables["SDL2IMAGE_GIF"] = self.options.gif
        tc.variables["SDL2IMAGE_BACKEND_IMAGEIO"] = self.options.get_safe("imageio", False)
        tc.variables["SDL2IMAGE_JPG"] = self.options.with_libjpeg
        tc.variables["SDL2IMAGE_LBM"] = self.options.lbm
        tc.variables["SDL2IMAGE_PCX"] = self.options.pcx
        tc.variables["SDL2IMAGE_PNG"] = self.options.with_libpng
        tc.variables["SDL2IMAGE_PNM"] = self.options.pnm
        tc.variables["SDL2IMAGE_SVG"] = self.options.svg
        tc.variables["SDL2IMAGE_TGA"] = self.options.tga
        tc.variables["SDL2IMAGE_TIF"] = self.options.with_libtiff
        tc.variables["SDL2IMAGE_WEBP"] = self.options.with_libwebp
        tc.variables["SDL2IMAGE_XCF"] = self.options.xcf
        tc.variables["SDL2IMAGE_XPM"] = self.options.xpm
        tc.variables["SDL2IMAGE_XV"] = self.options.xv
        # TODO: https://github.com/bincrafters/community/pull/1317#pullrequestreview-584847138
        tc.variables["SDL2IMAGE_TIF_SHARED"] = self.options.get_safe("with_libtiff_dynamic_load", False)
        tc.variables["SDL2IMAGE_JPG_SHARED"] = self.options.get_safe("with_libjpeg_dynamic_load", False)
        tc.variables["SDL2IMAGE_PNG_SHARED"] = self.options.get_safe("with_libpng_dynamic_load", False)
        tc.variables["SDL2IMAGE_WEBP_SHARED"] = self.options.get_safe("with_libwebp_dynamic_load", False)
        tc.variables["SDL_IS_SHARED"] = self.dependencies["sdl"].options.shared
        tc.generate()
        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        rmdir(self, os.path.join(self.source_folder, "external"))
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "COPYING.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SDL2_image")
        self.cpp_info.set_property("cmake_target_name", "SDL2_image::SDL2_image")
        if not self.options.shared:
            self.cpp_info.set_property("cmake_target_aliases", ["SDL2_image::SDL2_image-static"])
        self.cpp_info.set_property("pkg_config_name", "SDL2_image")
        # TODO: back to global scope in conan v2 once legacy generators removed
        self.cpp_info.components["_sdl_image"].libs = ["SDL2_image"]
        self.cpp_info.components["_sdl_image"].includedirs.append(os.path.join("include", "SDL2"))

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.names["cmake_find_package"] = "SDL2_image"
        self.cpp_info.names["cmake_find_package_multi"] = "SDL2_image"
        self.cpp_info.names["pkg_config"] = "SDL2_image"
        target_name = "SDL2_image" if self.options.shared else "SDL2_image-static"
        self.cpp_info.components["_sdl_image"].names["cmake_find_package"] = target_name
        self.cpp_info.components["_sdl_image"].names["cmake_find_package_multi"] = target_name
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
