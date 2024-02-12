from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


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

    def export_sources(self):
        if Version(self.version) < "2.6":
            copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not is_apple_os(self):
            del self.options.imageio
        if Version(self.version) < "2.6":
            del self.options.qoi
            del self.options.with_avif
            del self.options.with_jxl
        if self.settings.os != "Windows":
            del self.options.wic

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")
        if self.options.shared:
            # sdl static into sdl_image shared is not allowed
            self.options["sdl"].shared = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # Headers are exposed https://github.com/conan-io/conan-center-index/pull/16167#issuecomment-1508347351
        self.requires("sdl/2.28.3", transitive_headers=True)
        if self.options.with_libtiff:
            self.requires("libtiff/4.6.0")
        if self.options.with_libjpeg:
            self.requires("libjpeg/9e")
        if self.options.with_libpng:
            self.requires("libpng/1.6.40")
        if self.options.with_libwebp:
            self.requires("libwebp/1.3.2")
        if self.options.get_safe("with_avif"):
            self.requires("libavif/1.0.1")

    def validate(self):
        if self.options.shared and not self.dependencies["sdl"].options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} shared requires sdl shared")
        # TODO: libjxl doesn't support conan v2(yet)
        if self.options.get_safe("with_jxl"):
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support with_jxl (yet)")

    def build_requirements(self):
        if Version(self.version) >= "2.6":
            self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) < "2.6":
            tc.variables["SDL_IMAGE_SRC_DIR"] = self.source_folder.replace("\\", "/")
            tc.variables["BMP"] = self.options.bmp
            tc.variables["GIF"] = self.options.gif
            tc.variables["IMAGEIO"] = self.options.get_safe("imageio")
            tc.variables["JPG"] = self.options.with_libjpeg
            tc.variables["LBM"] = self.options.lbm
            tc.variables["PCX"] = self.options.pcx
            tc.variables["PNG"] = self.options.with_libpng
            tc.variables["PNM"] = self.options.pnm
            tc.variables["SVG"] = self.options.svg
            tc.variables["TGA"] = self.options.tga
            tc.variables["TIF"] = self.options.with_libtiff
            tc.variables["WEBP"] = self.options.with_libwebp
            tc.variables["XCF"] = self.options.xcf
            tc.variables["XPM"] = self.options.xpm
            tc.variables["XV"] = self.options.xv
            tc.variables["SDL_IS_SHARED"] = self.dependencies["sdl"].options.shared
        else:
            tc.variables["SDL2IMAGE_VENDORED"] = False
            tc.variables["SDL2IMAGE_DEPS_SHARED"] = False
            tc.variables["SDL2IMAGE_SAMPLES"] = False
            tc.variables["SDL2IMAGE_AVIF"] = self.options.get_safe("with_avif")
            tc.variables["SDL2IMAGE_BMP"] = self.options.bmp
            tc.variables["SDL2IMAGE_GIF"] = self.options.gif
            tc.variables["SDL2IMAGE_JPG"] = self.options.with_libjpeg
            tc.variables["SDL2IMAGE_JXL"] = self.options.get_safe("with_jxl")
            tc.variables["SDL2IMAGE_LBM"] = self.options.lbm
            tc.variables["SDL2IMAGE_PCX"] = self.options.pcx
            tc.variables["SDL2IMAGE_PNG"] = self.options.with_libpng
            tc.variables["SDL2IMAGE_PNM"] = self.options.pnm
            tc.variables["SDL2IMAGE_QOI"] = self.options.get_safe("qoi")
            tc.variables["SDL2IMAGE_SVG"] = self.options.svg
            tc.variables["SDL2IMAGE_TGA"] = self.options.tga
            tc.variables["SDL2IMAGE_TIF"] = self.options.with_libtiff
            tc.variables["SDL2IMAGE_WEBP"] = self.options.with_libwebp
            tc.variables["SDL2IMAGE_XCF"] = self.options.xcf
            tc.variables["SDL2IMAGE_XPM"] = self.options.xpm
            tc.variables["SDL2IMAGE_XV"] = self.options.xv
            tc.variables["SDL2IMAGE_BACKEND_WIC"] = self.options.get_safe("wic")
            tc.variables["SDL2IMAGE_BACKEND_IMAGEIO"] = self.options.get_safe("imageio")
        tc.generate()
        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        rmdir(self, os.path.join(self.source_folder, "external"))
        cmake = CMake(self)
        if Version(self.version) < "2.6":
            cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        else:
            cmake.configure()
        cmake.build()

        if Version(self.version) >= "2.6":
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "share"))

    def package(self):
        if Version(self.version) < "2.6":
            copy(self, "COPYING.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        else:
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
        if Version(self.version) >= "2.6":
            if self.settings.os == "Windows" and not self.options.shared:
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
        if self.options.get_safe("with_avif"):
            self.cpp_info.components["_sdl_image"].requires.append("libavif::libavif")
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
