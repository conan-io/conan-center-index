from conans import ConanFile, tools, CMake
import os


class SDL2ImageConan(ConanFile):
    name = "sdl2_image"
    description = "SDL_image is an image file loading library"
    topics = ("sdl2_image", "sdl_image", "sdl2", "sdl", "images", "opengl")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.libsdl.org/projects/SDL_image/"
    license = "MIT"
    exports_sources = ["CMakeLists.txt"]
    generators = ["cmake", "cmake_find_package_multi"]
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
        "jpg": [True, False],
        "tif": [True, False],
        "png": [True, False],
        "webp": [True, False],
        "imageio": [True, False]}
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
        "jpg": True,
        "tif": True,
        "png": True,
        "webp": True,
        "imageio": False
    }

    _cmake = None
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Macos":
            del self.options.imageio

    def requirements(self):
        self.requires("sdl/2.0.16")
        if self.options.tif:
            self.requires("libtiff/4.0.9")
        if self.options.jpg:
            self.requires("libjpeg/9d")
        if self.options.png:
            self.requires("libpng/1.6.37")
        if self.options.webp:
            self.requires("libwebp/1.0.3")
        self.requires("zlib/1.2.11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["BMP"] = self.options.bmp
        self._cmake.definitions["GIF"] = self.options.gif
        self._cmake.definitions["IMAGEIO"] = self.options.get_safe("imageio")
        self._cmake.definitions["JPG"] = self.options.jpg
        self._cmake.definitions["LBM"] = self.options.lbm
        self._cmake.definitions["PCX"] = self.options.pcx
        self._cmake.definitions["PNG"] = self.options.png
        self._cmake.definitions["PNM"] = self.options.pnm
        self._cmake.definitions["SVG"] = self.options.svg
        self._cmake.definitions["TGA"] = self.options.tga
        self._cmake.definitions["TIF"] = self.options.tif
        self._cmake.definitions["WEBP"] = self.options.webp
        self._cmake.definitions["XCF"] = self.options.xcf
        self._cmake.definitions["XPM"] = self.options.xpm
        self._cmake.definitions["XV"] = self.options.xv
        # TODO: https://github.com/bincrafters/community/pull/1317#pullrequestreview-584847138
        self._cmake.definitions["TIF_DYNAMIC"] = self.options["libtiff"].shared if self.options.tif else False
        self._cmake.definitions["JPG_DYNAMIC"] = self.options["libjpeg"].shared if self.options.jpg else False
        self._cmake.definitions["PNG_DYNAMIC"] = self.options["libpng"].shared if self.options.png else False
        self._cmake.definitions["WEBP_DYNAMIC"] = self.options["libwebp"].shared if self.options.webp else False
        self._cmake.definitions["SDL_IS_SHARED"] = self.options["sdl"].shared

        self._cmake.configure(build_dir="build")
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["SDL2_image"]
        self.cpp_info.includedirs.append(os.path.join("include", "SDL2"))
        # TODO: Add components in a sane way. SDL2_image might be incorrect, as the current dev version uses SDL2::image
        # The current dev version is the first version with official CMake support
        self.cpp_info.names["cmake_find_package"] = "SDL2_image"
        self.cpp_info.names["cmake_find_package_multi"] = "SDL2_image"
