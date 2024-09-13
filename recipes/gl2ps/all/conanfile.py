import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file

required_conan_version = ">=1.53.0"


class Gl2psConan(ConanFile):
    name = "gl2ps"
    description = "GL2PS: an OpenGL to PostScript printing library"
    license = "GL2PS OR LGPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.geuz.org/gl2ps/"
    topics = ("postscript", "opengl", "printing")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_png": [True, False],
        "with_zlib": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_png": True,
        "with_zlib": True,
    }

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
        self.requires("opengl/system", transitive_headers=True, transitive_libs=True)
        if self.options.with_png:
            self.requires("libpng/[>=1.6 <2]")
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["ENABLE_PNG"] = self.options.with_png
        tc.cache_variables["ENABLE_ZLIB"] = self.options.with_zlib
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "cmake_minimum_required(VERSION 2.8 FATAL_ERROR)",
                        "cmake_minimum_required(VERSION 3.15)")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING.GL2PS", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "COPYING.LGPL", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["gl2ps"]

        if self.options.with_png:
            self.cpp_info.defines.append("GL2PS_HAVE_LIBPNG")
        if self.options.with_zlib:
            self.cpp_info.defines.append("GL2PS_HAVE_ZLIB")
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines.append("GL2PSDLL")
