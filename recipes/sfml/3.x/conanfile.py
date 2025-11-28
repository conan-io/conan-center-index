from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.android import android_abi
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, rmdir, copy
import os

required_conan_version = ">=2.1"


class SfmlConan(ConanFile):
    name = "sfml"
    description = "Simple and Fast Multimedia Library."
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.sfml-dev.org"
    topics = ("multimedia", "games", "graphics", "audio")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        # modules
        "window": [True, False],
        "graphics": [True, False],
        "network": [True, False],
        "audio": [True, False],
        # window module options
        "opengl": ["es", "desktop"],
        # "use_drm": [True, False],  # Linux only, no support for now, PR welcome
        # "use_mesa3d": [True, False],  # Windows only, not available in CCI

    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "window": True,
        "graphics": True,
        "network": True,
        "audio": True,
        "opengl": "desktop",
    }
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")

        if not self.options.window:
            del self.options.opengl

        # As per CMakeLists.txt#L44, Android is always shared
        if self.settings.os == "Android":
            del self.options.shared
            del self.options.fPIC
            self.package_type = "shared-library"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.window:
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.requires("xorg/system")
                if self.settings.os == "Linux":
                    self.requires("libudev/system")

            if self.settings.os not in ("iOS", "Android"):  # Handled as a framework
                self.requires("opengl/system")
            self.requires("vulkan-headers/[~1]")

        if self.options.graphics:
            if self.settings.os == "Android" or self.settings.os == "iOS":
                self.requires("zlib/[>=1.2.11 <2]")
            if self.settings.os == "iOS":
                self.requires("bzip2/1.0.8")
            self.requires("freetype/2.13.2")
            self.requires("stb/[>=cci.20240531]")

        if self.options.audio:
            self.requires("vorbis/1.3.7")
            self.requires("flac/1.4.3")
            self.requires("minimp3/cci.20211201")
            self.requires("miniaudio/0.11.22", transitive_headers=True)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.24]")

    def validate(self):
        check_min_cppstd(self, 17)

        if self.options.graphics and not self.options.window:
            raise ConanInvalidConfiguration(f"-o={self.ref}:graphics=True requires -o={self.ref}:window=True")

        if self.settings.os == "Windows" and self.options.get_safe("shared") and self.settings.get_safe("compiler.runtime") == "static":
            raise ConanInvalidConfiguration(f"{self.ref} does not support shared libraries with static runtime")

    def validate_build(self):
        if self.settings.os == "Macos" and self.settings.compiler != "apple-clang":
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on {self.settings.os} with {self.settings.compiler}")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)

        tc.cache_variables["SFML_BUILD_WINDOW"] = self.options.window
        tc.cache_variables["SFML_BUILD_GRAPHICS"] = self.options.graphics
        tc.cache_variables["SFML_BUILD_NETWORK"] = self.options.network
        tc.cache_variables["SFML_BUILD_AUDIO"] = self.options.audio

        if self.options.window:
            tc.cache_variables["SFML_OPENGL_ES"] = self.options.opengl == "es"

        tc.cache_variables["SFML_GENERATE_PDB"] = False  # PDBs not allowed in CCI

        if self.settings.os == "Windows":
            tc.cache_variables["SFML_USE_STATIC_STD_LIBS"] = self.settings.get_safe("compiler.runtime") == "static"
            tc.cache_variables["SFML_USE_MESA3D"] = False  # self.options.use_mesa3d

        tc.cache_variables["SFML_USE_SYSTEM_DEPS"] = True

        tc.cache_variables["SFML_INSTALL_PKGCONFIG_FILES"] = False
        tc.cache_variables["SFML_WARNINGS_AS_ERRORS"] = False
        tc.cache_variables["SFML_CONFIGURE_EXTRAS"] = False

        # Tip: You can use this locally to test the extras when adding a new version,
        # uncomment both to build examples, or run them manually
        # tc.cache_variables["SFML_CONFIGURE_EXTRAS"] = True
        # tc.cache_variables["SFML_BUILD_EXAMPLES"] = True

        tc.generate()
        deps = CMakeDeps(self)
        if self.options.audio:
            deps.set_property("flac", "cmake_file_name", "FLAC")

        if self.options.graphics:
            deps.set_property("freetype", "cmake_file_name", "Freetype")
            deps.set_property("freetype", "cmake_target_name", "Freetype::Freetype")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "license.md", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def _basic_module_definition(self, name):
        self.cpp_info.components[name].set_property("cmake_target_name", f"SFML::{name.capitalize()}")

        libname = f"sfml-{name}"

        if self.package_type == "static-library" and name != "main":
            libname += "-s"
            self.cpp_info.components[name].defines = ["SFML_STATIC"]
        if self.settings.build_type == "Debug":
            libname += "-d"
        self.cpp_info.components[name].libs = [libname]

        # CMakeLists.txt#L87 - Android libs are in lib/<CMAKE_ANDROID_ARCH_ABI>
        if self.settings.os == "Android":
            self.cpp_info.components[name].libdirs = [os.path.join("lib", android_abi(self))]

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SFML")
        self.cpp_info.set_property("pkg_config_name", "sfml-all")

        modules = ["system"]
        if self.settings.os in ["Windows", "iOS", "Android"]:
            modules.append("main")

        modules.extend(module for module in ["window", "graphics", "network", "audio"] if self.options.get_safe(module))

        for module in modules:
            self._basic_module_definition(module)

        # System module is always required
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["system"].system_libs = ["pthread", "rt"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["system"].system_libs = ["winmm"]
        elif self.settings.os == "Android":
            self.cpp_info.components["system"].system_libs = ["log", "android"]

        if self.options.window:
            self.cpp_info.components["window"].requires = ["system", "vulkan-headers::vulkan-headers"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["window"].system_libs.append("dl")
                self.cpp_info.components["window"].requires.extend(["xorg::x11", "xorg::xrandr", "xorg::xcursor", "xorg::xi"])

            if self.settings.os == "iOS":
                self.cpp_info.components["window"].frameworks = ["OpenGLES"]
            elif self.settings.os == "Android":
                self.cpp_info.components["window"].system_libs.extend(["egl", "GLESv2"])
            else:
                self.cpp_info.components["window"].requires.append("opengl::opengl")

            if self.settings.os == "Linux":
                self.cpp_info.components["window"].requires.append("libudev::libudev")
            elif self.settings.os == "Windows":
                self.cpp_info.components["window"].system_libs.extend(["gdi32", "winmm"])
            elif self.settings.os == "FreeBSD":
                self.cpp_info.components["window"].system_libs.append("usbhid")
            elif self.settings.os == "Macos":
                # CoreServices is pulled from Carbon, even if it does not show up in the upstream CMakeLists.txt
                self.cpp_info.components["window"].frameworks = ["Foundation", "AppKit", "IOKit", "Carbon", "CoreServices"]
            elif self.settings.os == "iOS":
                self.cpp_info.components["window"].frameworks = ["Foundation", "UIKit", "CoreGraphics", "QuartzCore", "CoreMotion"]
            elif self.settings.os == "Android":
                self.cpp_info.components["window"].system_libs = ["android"]

        if self.options.graphics:
            self.cpp_info.components["graphics"].requires = ["window", "stb::stb"]
            if self.settings.os == "Android" or self.settings.os == "iOS":
                self.cpp_info.components["graphics"].requires.append("zlib::zlib")
            if self.settings.os == "iOS":
                self.cpp_info.components["graphics"].requires.append("bzip2::bzip2")
            self.cpp_info.components["graphics"].requires.append("freetype::freetype")

        if self.options.network:
            self.cpp_info.components["network"].requires = ["system"]

            if self.settings.os == "Windows":
                self.cpp_info.components["network"].system_libs = ["ws2_32"]

        if self.options.audio:
            self.cpp_info.components["audio"].requires = ["vorbis::vorbis", "flac::flac", "system", "minimp3::minimp3", "miniaudio::miniaudio"]
            if self.settings.os == "iOS":
                self.cpp_info.components["audio"].frameworks = ["Foundation", "CoreFoundation", "CoreAudio", "AudioToolbox", "AVFoundation"]
            else:
                self.cpp_info.components["audio"].requires.extend(["vorbis::vorbisfile", "vorbis::vorbisenc"])

            if self.settings.os == "Android":
                self.cpp_info.components["audio"].system_libs = ["android", "OpenSLES"]

            if self.settings.os == "Linux":
                self.cpp_info.components["audio"].system_libs = ["pthread", "dl"]
