from conans import ConanFile, tools, CMake
import functools
import os

required_conan_version = ">=1.43.0"


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
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Macos":
            del self.options.imageio

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BMP"] = self.options.bmp
        cmake.definitions["GIF"] = self.options.gif
        cmake.definitions["IMAGEIO"] = self.options.get_safe("imageio")
        cmake.definitions["JPG"] = self.options.with_libjpeg
        cmake.definitions["LBM"] = self.options.lbm
        cmake.definitions["PCX"] = self.options.pcx
        cmake.definitions["PNG"] = self.options.with_libpng
        cmake.definitions["PNM"] = self.options.pnm
        cmake.definitions["SVG"] = self.options.svg
        cmake.definitions["TGA"] = self.options.tga
        cmake.definitions["TIF"] = self.options.with_libtiff
        cmake.definitions["WEBP"] = self.options.with_libwebp
        cmake.definitions["XCF"] = self.options.xcf
        cmake.definitions["XPM"] = self.options.xpm
        cmake.definitions["XV"] = self.options.xv
        # TODO: https://github.com/bincrafters/community/pull/1317#pullrequestreview-584847138
        cmake.definitions["TIF_DYNAMIC"] = self.options["libtiff"].shared if self.options.with_libtiff else False
        cmake.definitions["JPG_DYNAMIC"] = self.options["libjpeg"].shared if self.options.with_libjpeg else False
        cmake.definitions["PNG_DYNAMIC"] = self.options["libpng"].shared if self.options.with_libpng else False
        cmake.definitions["WEBP_DYNAMIC"] = self.options["libwebp"].shared if self.options.with_libwebp else False
        cmake.definitions["SDL_IS_SHARED"] = self.options["sdl"].shared

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        tools.rmdir(os.path.join(self._source_subfolder, "external"))
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SDL2_image")
        self.cpp_info.set_property("cmake_target_name", "SDL2_image::SDL2_image")
        if not self.options.shared:
            self.cpp_info.set_property("cmake_target_aliases", ["SDL2_image::SDL2_image-static"])
        self.cpp_info.set_property("pkg_config_name", "SDL2_image")
        self.cpp_info.libs = ["SDL2_image"]
        self.cpp_info.includedirs.append(os.path.join("include", "SDL2"))

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.names["cmake_find_package"] = "SDL2_image"
        self.cpp_info.names["cmake_find_package_multi"] = "SDL2_image"
        self.cpp_info.names["pkg_config"] = "SDL2_image"
