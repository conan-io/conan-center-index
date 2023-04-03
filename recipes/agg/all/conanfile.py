from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.errors import ConanInvalidConfiguration

import os

required_conan_version = ">=1.52.0"

class AggConan(ConanFile):
    name = 'agg'
    description = 'AGG Anti-Grain Geometry Library'
    topics = ('graphics')
    url = "https://github.com/conan-io/conan-center-index"
    homepage = 'https://github.com/aggeom'
    license = 'BSD-3-Clause'

    settings = 'os', 'arch', 'compiler', 'build_type'
    options = {
        'shared': [True, False],
        'fPIC': [True, False],
        'with_gpc': [True, False],
        'with_freetype': [True, False],
        'with_agg2d': [True, False],
        'with_agg2d_freetype': [True, False],
        'with_platform': [True, False],
        'with_controls': [True, False],
    }

    default_options = {
        'shared': False,
        'fPIC': True,
        'with_gpc': True,
        'with_freetype': True,
        'with_agg2d': True,
        'with_agg2d_freetype': True,
        'with_platform': True,
        'with_controls': True,
    }

    def validate(self):
        if self.settings.os == "Macos":
            raise ConanInvalidConfiguration("Unsupported os")
        if self.options.shared:
            raise ConanInvalidConfiguration("Invalid configuration")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_freetype:
            self.requires('freetype/2.13.0')
        if self.options.with_platform and self.settings.os in ["Linux"]:
            self.requires("xorg/system")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables['agg_USE_EXPAT'] = False
        tc.variables['agg_USE_SDL_PLATFORM'] = False
        tc.variables['agg_BUILD_DEMO'] = False
        tc.variables['agg_BUILD_EXAMPLES'] = False
    
        tc.variables['agg_USE_GPC'] = self.options.with_gpc
        tc.variables['agg_USE_FREETYPE'] = self.options.with_freetype
        tc.variables['agg_USE_AGG2D'] = self.options.with_agg2d
        tc.variables['agg_USE_AGG2D_FREETYPE'] = self.options.with_agg2d_freetype
        tc.variables['agg_BUILD_PLATFORM'] = self.options.with_platform
        tc.variables['agg_BUILD_CONTROLS'] = self.options.with_controls

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, src=self.source_folder, pattern='LICENSE', dst='licenses')
        cmake = CMake(self)
        cmake.configure()
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):

        self.cpp_info.set_property("cmake_file_name", "agg")

        lib_suffix = "d" if self.settings.build_type == "Debug" and self.options.debug_suffix else ""

        self.cpp_info.components["agg"].set_property("cmake_target_name", "agg::agg")
        self.cpp_info.components["agg"].libs = ["agg" + lib_suffix]
        self.cpp_info.components["agg"].includedirs = [os.path.join("include", "agg")]

        if self.options.with_freetype:
            self.cpp_info.components["fontfreetype"].set_property("cmake_target_name", "agg::fontfreetype")
            self.cpp_info.components["fontfreetype"].libs = ["aggfontfreetype" + lib_suffix]
            self.cpp_info.components["fontfreetype"].includedirs = [os.path.join("include", "agg","fontfreetype")]
            self.cpp_info.components["2d"].requires = ["agg"]
            
        if self.options.with_gpc:
            self.cpp_info.components["gpc"].set_property("cmake_target_name", "agg::gpc")
            self.cpp_info.components["gpc"].libs = [ "agggpc" + lib_suffix]
            self.cpp_info.components["gpc"].includedirs = [os.path.join("include", "agg","gpc")]


        if self.options.with_agg2d:
            self.cpp_info.components["2d"].set_property("cmake_target_name", "agg::2d")
            self.cpp_info.components["2d"].libs = ["agg2d" + lib_suffix]
            self.cpp_info.components["2d"].includedirs = [os.path.join("include", "agg","2d")]
            self.cpp_info.components["2d"].requires = ["agg"]
            if self.options.with_agg2d_freetype:
                self.cpp_info.components["2d"].requires = ["agg", "fontfreetype"]

        if self.options.with_platform:
            
            self.cpp_info.components["platform"].set_property("cmake_target_name", "agg::platform")
            self.cpp_info.components["platform"].libs = ["aggplatform" + lib_suffix]
            self.cpp_info.components["platform"].includedirs = [os.path.join("include", "agg","platform")]
            if self.settings.os in ["Linux"]:
                self.cpp_info.components["platform"].requires = ["xorg::xorg", "agg"]

        if self.options.with_controls:
            self.cpp_info.components["controls"].set_property("cmake_target_name", "agg::controls")
            self.cpp_info.components["controls"].libs = ["aggctrl" + lib_suffix]
            self.cpp_info.components["controls"].includedirs = [os.path.join("include", "agg","ctrl")]
            self.cpp_info.components["controls"].requires = ["agg"]
