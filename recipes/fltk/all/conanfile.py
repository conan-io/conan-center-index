import os

from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get, rm, rmdir

required_conan_version = ">=1.53.0"


class FltkConan(ConanFile):
    name = "fltk"
    description = "Fast Light Toolkit is a cross-platform C++ GUI toolkit"
    license = "LGPL-2.0-custom"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.fltk.org"
    topics = ("gui",)

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_gl": [True, False],
        "with_threads": [True, False],
        "with_gdiplus": [True, False],
        "abi_version": ["ANY"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_gl": True,
        "with_threads": True,
        "with_gdiplus": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            self.options.rm_safe("with_gdiplus")

        if self.options.abi_version == None:
            _version_token = self.version.split(".")
            _version_major = int(_version_token[0])
            if len(_version_token) >= 3:
                _version_minor = int(_version_token[1])
                _version_patch = int(_version_token[2])
            elif len(_version_token) >= 2:
                _version_minor = int(_version_token[1])
                _version_patch = 0
            self.options.abi_version = str(
                int(_version_major) * 10000 + int(_version_minor) * 100 + int(_version_patch)
            )

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/1.2.13")
        self.requires("libjpeg/9e")
        self.requires("libpng/1.6.40")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("opengl/system")
            self.requires("glu/system")
            self.requires("fontconfig/2.14.2")
            self.requires("xorg/system")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["OPTION_BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["FLTK_BUILD_TEST"] = False
        tc.variables["FLTK_BUILD_EXAMPLES"] = False
        tc.variables["OPTION_USE_GL"] = self.options.with_gl
        tc.variables["OPTION_USE_THREADS"] = self.options.with_threads
        tc.variables["OPTION_BUILD_HTML_DOCUMENTATION"] = False
        tc.variables["OPTION_BUILD_PDF_DOCUMENTATION"] = False
        if self.options.abi_version:
            tc.variables["OPTION_ABI_VERSION"] = self.options.abi_version
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "FLTK.framework"))
        rmdir(self, os.path.join(self.package_folder, "CMake"))
        rm(self, "fltk-config*", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "fltk")
        self.cpp_info.set_property("cmake_target_name", "fltk::fltk")
        self.cpp_info.libs = collect_libs(self)

        if self.options.shared and self.settings.os == "Windows":
            self.cpp_info.defines.append("FL_DLL")
        if self.settings.os in ("Linux", "FreeBSD"):
            if self.options.with_threads:
                self.cpp_info.system_libs.extend(["pthread", "dl"])
            if self.options.with_gl:
                self.cpp_info.system_libs.extend(["GL", "GLU"])
        if is_apple_os(self):
            self.cpp_info.frameworks = [
                "AppKit", "ApplicationServices", "Carbon", "Cocoa", "CoreFoundation", "CoreGraphics",
                "CoreText", "CoreVideo", "Foundation", "IOKit", "OpenGL",
            ]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["gdi32", "imm32", "msimg32", "ole32", "oleaut32", "uuid"]
            if self.options.get_safe("with_gdiplus"):
                self.cpp_info.system_libs.append("gdiplus")

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.names["cmake_find_package"] = "fltk"
        self.cpp_info.names["cmake_find_package_multi"] = "fltk"
