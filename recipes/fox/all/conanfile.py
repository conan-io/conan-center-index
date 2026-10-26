from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os


required_conan_version = ">=2.0.9"


class FoxConan(ConanFile):
    name = "fox"
    description = "FOX is a C++ based Toolkit for developing Graphical User Interfaces."
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://fox-toolkit.org"
    topics = ("GUI",)
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_jpeg": [True, False],
        "with_png": [True, False],
        "with_tiff": [True, False],
        "with_zlib": [True, False],
        "with_bz2": [True, False],
        "with_webp": [True, False],
        "with_jp2": [True, False],
        "with_opengl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_jpeg": True,
        "with_png": True,
        "with_tiff": True,
        "with_zlib": True,
        "with_bz2": True,
        "with_webp": True,
        "with_jp2": True,
        "with_opengl": True,
    }
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        for dir in (".", "src", "utils"):
            copy(self, "CMakeLists.txt", os.path.join(self.recipe_folder, "cmake", dir),
                 os.path.join(self.export_sources_folder, dir))

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        if self.options.with_jpeg:
            self.requires("libjpeg/9f")
        if self.options.with_png:
            self.requires("libpng/1.6.58")
        if self.options.with_tiff:
            self.requires("libtiff/4.6.0")
        if self.options.with_zlib:
            self.requires("zlib/1.3.2")
        if self.options.with_bz2:
            self.requires("bzip2/1.0.8")
        if self.options.with_webp:
            self.requires("libwebp/1.3.2")
        if self.options.with_jp2:
            self.requires("openjpeg/2.5.2")
        if self.options.with_opengl:
            self.requires("opengl/system")
            self.requires("glu/system")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["WITH_JPEG"] = self.options.with_jpeg
        tc.cache_variables["WITH_PNG"] = self.options.with_png
        tc.cache_variables["WITH_TIFF"] = self.options.with_tiff
        tc.cache_variables["WITH_ZLIB"] = self.options.with_zlib
        tc.cache_variables["WITH_BZ2LIB"] = self.options.with_bz2
        tc.cache_variables["WITH_WEBP"] = self.options.with_webp
        tc.cache_variables["WITH_OPENJPEG"] = self.options.with_jp2
        tc.cache_variables["WITH_OPENGL"] = self.options.with_opengl
        tc.generate()
        CMakeDeps(self).generate()

    def build(self):
        for dir in (".", "src", "utils"):
            copy(self, "CMakeLists.txt", os.path.join(self.export_sources_folder, dir),
                 os.path.join(self.source_folder, dir))
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE*", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["fox-1.6"]                 # libfox-1.6.so / fox-1.6.lib
        self.cpp_info.includedirs = ["include/fox-1.6"]  # FOX installs headers here, not include/

        # TODO we should check whether the GL libs are already pulled in via the opengl recipe
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = [
                "X11", "Xext", "Xft", "Xcursor", "Xrandr", "Xrender",
                "Xfixes", "Xi", "fontconfig", "freetype", "dl", "pthread", "rt",
            ]
            if self.options.get_safe("with_opengl"):
                self.cpp_info.system_libs += ["GL", "GLU"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = [
                "gdi32", "user32", "comctl32", "ws2_32", "winspool",
                "mpr", "imm32", "shell32", "ole32", "uuid",
            ]
            if self.options.get_safe("with_opengl"):
                self.cpp_info.system_libs += ["opengl32", "glu32"]
        elif self.settings.os == "Macos":
            # the OpenGL framework is already activated via the opengl recipe
            self.cpp_info.frameworks = ["CoreFoundation", "Cocoa"]
