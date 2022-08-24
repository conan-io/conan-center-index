from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=1.47.0"


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
        "with_libtiff": [True, False],
        "with_libpng": [True, False],
        "with_libwebp": [True, False],
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
        "with_libtiff": True,
        "with_libpng": True,
        "with_libwebp": True,
        "imageio": False,
    }

    exports_sources = "CMakeLists.txt"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Macos":
            del self.options.imageio

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def requirements(self):
        self.requires("sdl/2.0.20")
        if self.options.with_libtiff:
            self.requires("libtiff/4.3.0")
        if self.options.with_libjpeg:
            self.requires("libjpeg/9d")
        if self.options.with_libpng:
            self.requires("libpng/1.6.37")
        if self.options.with_libwebp:
            self.requires("libwebp/1.2.2")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
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
        # TODO: https://github.com/bincrafters/community/pull/1317#pullrequestreview-584847138
        tc.variables["TIF_DYNAMIC"] = self.dependencies["libtiff"].options.shared if self.options.with_libtiff else False
        tc.variables["JPG_DYNAMIC"] = self.dependencies["libjpeg"].options.shared if self.options.with_libjpeg else False
        tc.variables["PNG_DYNAMIC"] = self.dependencies["libpng"].options.shared if self.options.with_libpng else False
        tc.variables["WEBP_DYNAMIC"] = self.dependencies["libwebp"].options.shared if self.options.with_libwebp else False
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
        self.cpp_info.libs = ["SDL2_image"]
        self.cpp_info.includedirs.append(os.path.join("include", "SDL2"))

        # TODO: to remove, tt's a workaround to support conan v1 generators
        # (fixed in conan 1.51.1 by https://github.com/conan-io/conan/pull/11790)
        self.cpp_info.requires = ["sdl::sdl"]
        if self.options.with_libtiff:
            self.cpp_info.requires.append("libtiff::libtiff")
        if self.options.with_libjpeg:
            self.cpp_info.requires.append("libjpeg::libjpeg")
        if self.options.with_libpng:
            self.cpp_info.requires.append("libpng::libpng")
        if self.options.with_libwebp:
            self.cpp_info.requires.append("libwebp::libwebp")

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.names["cmake_find_package"] = "SDL2_image"
        self.cpp_info.names["cmake_find_package_multi"] = "SDL2_image"
        self.cpp_info.names["pkg_config"] = "SDL2_image"
