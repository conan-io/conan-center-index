import os

from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.microsoft import msvc_runtime_flag
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class FltkConan(ConanFile):
    name = "fltk"
    description = "Fast Light Toolkit is a cross-platform C++ GUI toolkit"
    license = "LGPL-2.1-or-later WITH FLTK-exception"
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
        "with_xft": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_gl": True,
        "with_threads": True,
        "with_gdiplus": True,
        "with_xft": False,
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
            _version_minor = int(_version_token[1])
            _version_patch = int(_version_token[2]) if len(_version_token) >= 3 else 0
            self.options.abi_version = str(
                int(_version_major) * 10000 + int(_version_minor) * 100 + int(_version_patch)
            )

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("libjpeg/9e")
        self.requires("libpng/[>=1.6 <2]")
        # If Version >= 1.4.1, it also depends on FLTK_BACKEND_X11, but it's not introduced
        # in the recipe for now
        if not is_apple_os(self):
            self.requires("fontconfig/2.15.0")
        if self.settings.os in ["Linux", "FreeBSD"]:
            if self.options.with_gl:
                self.requires("opengl/system")
                self.requires("glu/system")
            self.requires("xorg/system")
            if self.options.with_xft:
                self.requires("libxft/2.3.8")
            if Version(self.version) >= "1.4.0":
                self.requires("gtk/system", options={"version": "3"})
                self.requires("wayland/1.22.0")
                self.requires("xkbcommon/1.6.0")
                self.requires("dbus/1.15.8")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FLTK_BUILD_TEST"] = False
        tc.variables["FLTK_BUILD_EXAMPLES"] = False
        if Version(self.version) < "1.4.0":
            tc.variables["OPTION_BUILD_SHARED_LIBS"] = self.options.shared
            tc.variables["OPTION_USE_GL"] = self.options.with_gl
            tc.variables["OPTION_USE_THREADS"] = self.options.with_threads
            tc.variables["OPTION_BUILD_HTML_DOCUMENTATION"] = False
            tc.variables["OPTION_BUILD_PDF_DOCUMENTATION"] = False
            tc.variables["OPTION_USE_XFT"] = self.options.with_xft
            if self.options.abi_version:
                tc.variables["OPTION_ABI_VERSION"] = self.options.abi_version
            tc.variables["OPTION_USE_SYSTEM_LIBJPEG"] = True
            tc.variables["OPTION_USE_SYSTEM_ZLIB"] = True
            tc.variables["OPTION_USE_SYSTEM_LIBPNG"] = True
        else:
            tc.variables["FLTK_BUILD_SHARED_LIBS"] = self.options.shared
            tc.variables["FLTK_BUILD_GL"] = self.options.with_gl
            tc.variables["FLTK_USE_PTHREADS"] = self.options.with_threads
            tc.variables["FLTK_BUILD_HTML_DOCS"] = False
            tc.variables["FLTK_BUILD_PDF_DOCS"] = False
            tc.variables["FLTK_USE_XFT"] = self.options.with_xft
            if self.options.abi_version:
                tc.variables["FLTK_ABI_VERSION"] = self.options.abi_version
            tc.variables["FLTK_USE_SYSTEM_LIBJPEG"] = True
            tc.variables["FLTK_USE_SYSTEM_ZLIB"] = True
            tc.variables["FLTK_USE_SYSTEM_LIBPNG"] = True
            tc.variables["FLTK_BUILD_FLUID"] = False
        if self.settings.compiler.get_safe("runtime") is not None:
            tc.variables["FLTK_MSVC_RUNTIME_DLL"] = "MT" not in msvc_runtime_flag(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
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

        if self.settings.os in ("Linux", "FreeBSD"):
            if self.options.with_threads:
                self.cpp_info.system_libs.extend(["pthread", "dl"])
            if self.options.with_gl:
                self.cpp_info.system_libs.extend(["GL", "GLU"])
        elif is_apple_os(self):
            self.cpp_info.frameworks = [
                "AppKit", "ApplicationServices", "Carbon", "Cocoa", "CoreFoundation", "CoreGraphics",
                "CoreText", "CoreVideo", "Foundation", "IOKit",
            ]
            if self.options.with_gl:
                self.cpp_info.frameworks.append("OpenGL")
        elif self.settings.os == "Windows":
            if self.options.shared:
                self.cpp_info.defines.append("FL_DLL")
            self.cpp_info.system_libs = ["gdi32", "imm32", "msimg32", "ole32", "oleaut32", "uuid", "comctl32"]
            if self.options.get_safe("with_gdiplus"):
                self.cpp_info.system_libs.append("gdiplus")
            if self.options.with_gl:
                self.cpp_info.system_libs.append("opengl32")
            if Version(self.version) >= "1.4.0":
                self.cpp_info.system_libs.append("ws2_32")
