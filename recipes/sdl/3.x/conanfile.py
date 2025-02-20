from conan import ConanFile, conan_version
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, replace_in_file, rm, rmdir, copy
from conan.tools.gnu import PkgConfigDeps
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.env import Environment

import os

required_conan_version = ">=1.55.0"

# Subsystems, CMakeLists.txt#L234
_subsystems = [
    ("audio", []),
    ("video", []),
    ("gpu", ["video"]),
    ("render", ["video"]),
    ("camera", ["video"]),
    ("joystick", []),
    ("haptic", ["joystick"]),
    ("hidapi", []),
    ("power", []),
    ("sensor", []),
    ("dialog", []),
]

class SDLConan(ConanFile):
    name = "sdl"
    description = "A cross-platform development library designed to provide low level access to audio, keyboard, mouse, joystick, and graphics hardware"
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.libsdl.org"
    topics = ("sdl3", "audio", "keyboard", "graphics", "opengl")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        **{
            "shared": [True, False],
            "fPIC": [True, False],
        },
        **{subsystem: [True, False] for subsystem, _ in _subsystems},
        **{
            "alsa": [True, False],
            "pulseaudio": [True, False],
            "sndio": [True, False],
            "opengl": [True, False],
            "opengles": [True, False],
            "x11": [True, False],
            "xcursor": [True, False],
            "xdbe": [True, False],
            "xinput": [True, False],
            "xfixes": [True, False],
            "xrandr": [True, False],
            "xscrnsaver": [True, False],
            "xshape": [True, False],
            "xsync": [True, False],
            "wayland": [True, False],
            "vulkan": [True, False],
            "metal": [True, False],
            "directx": [True, False],
            "libudev": [True, False],
            "dbus": [True, False],
            "libusb": [True, False],
        }
    }

    default_options = {
        **{
            "shared": False,
            "fPIC": True,
        },
        **{subsystem: True for subsystem, _ in _subsystems},
        **{
            ## Audio
            # Linux only
            "alsa": True,
            "pulseaudio": True,
            "sndio": True,
            ## Video
            "opengl": True,  # TODO: Off by default in apple_os
            "opengles": True,
            "x11": True,
            "xcursor": True,
            "xdbe": True,
            "xinput": True,
            "xfixes": True,
            "xrandr": True,
            "xscrnsaver": True,
            "xshape": True,
            "xsync": True,
            "wayland": True,
            "vulkan": True,
            "metal": True,
            "directx": True,
            ## Hidapi
            "libusb": True,
            ## Other
            "libudev": True,
            "dbus": True,
        }
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        if self.settings.os != "Linux":
            del self.options.pulseaudio
            del self.options.alsa
            del self.options.sndio
            del self.options.libudev
            del self.options.dbus # TODO: maybe use _is_unix_sys
            del self.options.x11
            del self.options.xcursor
            del self.options.xdbe
            del self.options.xinput
            del self.options.xfixes
            del self.options.xrandr
            del self.options.xscrnsaver
            del self.options.xshape
            del self.options.xsync
            del self.options.wayland

        if not is_apple_os(self):
            del self.options.metal

        if self.settings.os != "Windows":
            del self.options.directx

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

        if not (self.settings.os == "Android" and self.options.get_safe("hidapi")):
            self.settings.rm_safe("compiler.libcxx")
            self.settings.rm_safe("compiler.cppstd")

        if not self.options.get_safe("audio"):
            self.options.rm_safe("alsa")
            self.options.rm_safe("pulseaudio")
            self.options.rm_safe("sndio")

        if not self.options.get_safe("video"):
            self.options.rm_safe("opengl")
            self.options.rm_safe("opengles")
            self.options.rm_safe("x11")
            self.options.rm_safe("wayland")
            self.options.rm_safe("vulkan")
            self.options.rm_safe("metal")

        if not self.options.get_safe("x11"):
            self.options.rm_safe("xcursor")
            self.options.rm_safe("xdbe")
            self.options.rm_safe("xinput")
            self.options.rm_safe("xfixes")
            self.options.rm_safe("xrandr")
            self.options.rm_safe("xscrnsaver")
            self.options.rm_safe("xshape")
            self.options.rm_safe("xsync")

        if not self.options.get_safe("hidapi"):
            self.options.rm_safe("libusb")

    def validate(self):
        # If any of the subsystems is enabled, then the corresponding dependencies must be enabled
        for subsystem, dependencies in _subsystems:
            if self.options.get_safe(subsystem):
                for dependency in dependencies:
                    if not self.options.get_safe(dependency):
                        raise ConanInvalidConfiguration(f'-o="&:{subsystem}=True" subsystem requires -o="&:{dependency}=True"')

    def validate_build(self):
        # TODO: Remove this, but only after recipe develop is finished
        if conan_version >= "2.12" and self._needs_libusb and self.dependencies["libusb"].options.get_safe("shared", True)\
                and not self.conf.get("tools.cmake.cmakedeps:new"):
            raise ConanInvalidConfiguration("SDL with shared libusb requires new CMakeDeps generator")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _is_unix_sys(self):
        """ True for UNIX but not Macos/Android"""
        # CMakeLists.txt#L110
        return self.settings.os in ("Linux", "FreeBSD")

    @property
    def _needs_libusb(self):
        # CMakeLists.txt#L134
        return (self.options.get_safe("libusb") and
                (not is_apple_os(self) or self.settings.os == "Macos") and
                self.settings.os != "Android")

    @property
    def _supports_opengl(self):
        # CMakeLists.txt#L331
        return (self.options.get_safe("opengl")
                and self.settings.os not in ("iOS", "visionOS", "tvOS", "watchOS"))

    @property
    def _supports_opengles(self):
        # CMakeLists.txt#L332
        return (self.options.get_safe("opengles")
                # and self.settings.os not in ("visionOS", "tvOS", "watchOS"))
                and self.settings.os == "Android")

    @property
    def _supports_dbus(self):
        # CMakeLists.txt#292
        return self.options.get_safe("dbus") and self._is_unix_sys

    def requirements(self):
        # TODO: understand if we want to make this an option
        self.requires("libiconv/1.17")
        if self._needs_libusb:
            self.requires("libusb/1.0.26")
        if self._supports_opengl:
            self.requires("opengl/system")
        if self.options.get_safe("libudev"):
            self.requires("libudev/system")
        if self._supports_dbus:
            self.requires("dbus/1.15.8")
        if self.options.get_safe("pulseaudio"):
            self.requires("pulseaudio/17.0")
        if self.options.get_safe("alsa"):
            self.requires("libalsa/1.2.12")
        if self.options.get_safe("sndio"):
            self.requires("libsndio/1.9.0")
        if self.options.get_safe("wayland"):
            self.requires("wayland/1.22.0")
            self.requires("xkbcommon/1.6.0")
            self.requires("egl/system")
        if self.options.get_safe("x11"):
            self.requires("xorg/system")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.24 <4]")
        if self.settings.os == "Linux" and not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        if self.options.get_safe("wayland"):
            self.tool_requires("wayland/<host_version>")  # Provides wayland-scanner

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["SDL_SHARED"] = self.options.shared
        tc.cache_variables["SDL_STATIC"] = not self.options.shared
        # Todo: Remove after recipe develop is finished
        tc.cache_variables["SDL_TEST_LIBRARY"] = True
        tc.cache_variables["SDL_TESTS"] = True
        tc.cache_variables["SDL_EXAMPLES"] = True
        tc.cache_variables["SDL_INSTALL_EXAMPLES"] = True
        tc.cache_variables["CMAKE_TRY_COMPILE_CONFIGURATION"] = str(self.settings.build_type)
        tc.cache_variables["SDL_SYSTEM_ICONV_DEFAULT"] = True
        tc.cache_variables["SDL_LIBICONV"] = True

        tc.cache_variables["SDL_JACK"] = False # Jack is not available in CCI

        for subsystem in _subsystems:
            tc.cache_variables[f"SDL_{subsystem[0].upper()}"] = self.options.get_safe(subsystem[0])

        if self._supports_opengl:
            tc.cache_variables["SDL_OPENGL"] = True
        if self._supports_opengles:
            tc.cache_variables["SDL_OPENGLES"] = True
        if self._needs_libusb:
            tc.cache_variables["SDL_HIDAPI_LIBUSB"] = True
            # TODO: This is a supported configuration in upstream
            tc.cache_variables["SDL_HIDAPI_LIBUSB_SHARED"] = self.dependencies["libusb"].options.get_safe("shared", True)

        tc.variables["SDL_VULKAN"] = self.options.get_safe("vulkan")
        tc.variables["SDL_METAL"] = self.options.get_safe("metal")
        tc.variables["SDL_DIRECTX"] = self.options.get_safe("directx")

        if self.options.get_safe("pulseaudio"):
            tc.cache_variables["SDL_PULSEAUDIO"] = True
            tc.cache_variables["SDL_PULSEAUDIO_SHARED"] = self.dependencies["pulseaudio"].options.get_safe("shared", True)
        if self.options.get_safe("alsa"):
            tc.cache_variables["SDL_ALSA"] = True
            tc.cache_variables["SDL_ALSA_SHARED"] = self.dependencies["libalsa"].options.shared
        if self.options.get_safe("sndio"):
            tc.cache_variables["SDL_SNDIO"] = True
            tc.cache_variables["SDL_SNDIO_SHARED"] = True  # sndio is always shared
        tc.cache_variables["SDL_LIBUDEV"] = self.options.get_safe("libudev", False)


        # X11 and wayland configuration
        with_x11 = self.options.get_safe("x11", False)
        tc.cache_variables["SDL_X11"] = with_x11
        tc.cache_variables["SDL_X11_SHARED"] = True
        if with_x11:
            # See https://github.com/bincrafters/community/issues/696
            tc.cache_variables["SDL_VIDEO_DRIVER_X11_SUPPORTS_GENERIC_EVENTS"] = 1
            tc.cache_variables["SDL_X11_XCURSOR"] = self.options.xcursor
            tc.cache_variables["SDL_X11_XDBE"] = self.options.xdbe
            tc.cache_variables["SDL_X11_XINPUT"] = self.options.xinput
            tc.cache_variables["SDL_X11_XFIXES"] = self.options.xfixes
            tc.cache_variables["SDL_X11_XRANDR"] = self.options.xrandr
            tc.cache_variables["SDL_X11_XSCRNSAVER"] = self.options.xscrnsaver
            tc.cache_variables["SDL_X11_XSHAPE"] = self.options.xshape
            tc.cache_variables["SDL_X11_XSYNC"] = self.options.xsync

        with_wayland = self.options.get_safe("wayland", False)
        tc.cache_variables["SDL_WAYLAND"] = with_wayland
        if with_wayland:
            tc.cache_variables["SDL_WAYLAND_SHARED"] = self.dependencies["wayland"].options.shared
        if not with_x11 and not with_wayland:
            # Disable windowing support:
            # https://github.com/libsdl-org/SDL/blob/main/docs/README-cmake.md#cmake-fails-to-build-without-x11-or-wayland-support
            tc.cache_variables["SDL_UNIX_CONSOLE_BUILD"] = True

        tc.generate()
        deps = CMakeDeps(self)
        deps.set_property("libusb", "cmake_target_name", "LibUSB::LibUSB")
        deps.set_property("libusb", "cmake_file_name", "LibUSB")
        deps.generate()
        pcdeps = PkgConfigDeps(self)
        pcdeps.generate()

    def _patch_sources(self):
        # TODO: Once new CMakeDeps is default, remove this
        if not self.conf.get("tools.cmake.cmakedeps:new"):
            replace_in_file(self, os.path.join(self.source_folder, "cmake", "sdlchecks.cmake"),
                            "target_get_dynamic_library(dynamic_libusb LibUSB::LibUSB)",
                            "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    @property
    def _is_clang_cl(self):
        return self.settings.os == "Windows" and self.settings.compiler == "clang" and \
            self.settings.compiler.get_safe("runtime")

    def package_info(self):
        sdl_lib_name = "SDL3"
        if (is_msvc(self) or self._is_clang_cl) and not self.options.shared:
            sdl_lib_name = f"{sdl_lib_name}-static"
        self.cpp_info.libs = [sdl_lib_name]
        self.cpp_info.set_property("cmake_file_name", "SDL3")
        self.cpp_info.set_property("cmake_target_name", "SDL3::SDL3")
        self.cpp_info.set_property("cmake_target_aliases", ["SDL3::SDL3-shared" if self.options.shared else "SDL3::SDL3-static"])
        # CMakeLists.txt#L120
        if self.settings.os in ("Linux", "FreeBSD", "Macos"):
            self.cpp_info.system_libs.append("pthread")

        # TODO: dl support in Unix/Macos, CMakeLists.txt#L1209
        # TODO: Android support of opengles if video is enabled, CMakeLists.txt#L1349

        # CMakeLists.txt#L327
        self.cpp_info.requires.append("libiconv::libiconv")

        # TODO: check conditions
        if self.options.get_safe("libudev"):
            self.cpp_info.requires.append("libudev::libudev")

        if self._needs_libusb:
            self.cpp_info.requires.append("libusb::libusb")

        if self.options.get_safe("dbus"):
            self.cpp_info.requires.append("dbus::dbus")

        if self.options.get_safe("opengl"):
            self.cpp_info.requires.append("opengl::opengl")

        if self.options.get_safe("wayland"):
            self.cpp_info.requires.extend(["wayland::wayland", "xkbcommon::xkbcommon", "egl::egl"])

        if self.options.get_safe("x11"):
            self.cpp_info.requires.extend(["xorg::x11", "xorg::xext"])
            # xdbe, xshape and xsync are covered by x11 and xext
            if self.options.xcursor:
                self.cpp_info.requires.append("xorg::xcursor")
            if self.options.xinput:
                self.cpp_info.requires.append("xorg::xi")
            if self.options.xfixes:
                self.cpp_info.requires.append("xorg::xfixes")
            if self.options.xrandr:
                self.cpp_info.requires.append("xorg::xrandr")
            if self.options.xscrnsaver:
                self.cpp_info.requires.append("xorg::xscrnsaver")

        # TODO: Link opengles
        if self._supports_opengles:
            self.cpp_info.system_libs.extend(["GLESv1_CM", "GLESv2", "OpenSLES"])

        if self.options.get_safe("audio"):
            if self.options.get_safe("alsa"):
                self.cpp_info.requires.append("libalsa::libalsa")
            if self.options.get_safe("pulseaudio"):
                self.cpp_info.requires.append("pulseaudio::pulseaudio")
            if self.options.get_safe("sndio"):
                self.cpp_info.requires.append("libsndio::libsndio")

        # TODO: could it work with shared?
        if is_apple_os(self) and not self.options.shared:
            self.cpp_info.frameworks = ["CoreVideo", "Foundation"]

            if self.settings.os == "Macos":
                self.cpp_info.frameworks.extend(["Cocoa", "Carbon"])

            if self.options.get_safe("audio"):
                self.cpp_info.frameworks.extend(["CoreAudio", "AudioToolbox", "AVFoundation"])

            if self.options.get_safe("video"):
                if self.settings.os in ("iOS", "tvOS", "visionOS", "watchOS"):
                    self.cpp_info.frameworks.extend(["CoreGraphics", "QuartzCore", "UIKit"])
                else:
                    self.cpp_info.frameworks.append("UniformTypeIdentifiers")

            if self.options.get_safe("camera") and self.settings.os in ("Macos", "iOS"):
                self.cpp_info.frameworks.append("CoreMedia")

            if self.options.get_safe("joystick"):
                self.cpp_info.frameworks.append("GameController")
                self.cpp_info.sharedlinkflags.append("-Wl,-weak_framework,CoreHaptics")
                self.cpp_info.exelinkflags.append("-Wl,-weak_framework,CoreHaptics")
                if self.settings.os == "Macos":
                    # Mind that ForceFeedback is also added in haptic system, but haptic depends on joystick
                    self.cpp_info.frameworks.extend(["ForceFeedback", "IOKit"])
                elif self.settings.os in ("iOS", "visionOS", "watchOS"):
                    self.cpp_info.frameworks.append("CoreMotion")

            if self.options.get_safe("hidapi") and self.settings.os in ("iOS", "tvOS"):
                self.cpp_info.frameworks.append("CoreBluetooth")

            if self.options.get_safe("power") and self.settings.os == "Macos":
                self.cpp_info.frameworks.append("IOKit")

            if self.options.get_safe("opengles") and self.settings.os in ("iOS", "tvOS", "visionOS", "watchOS"):
                self.cpp_info.frameworks.append("OpenGLES")

            if self.options.get_safe("metal"):
                self.cpp_info.frameworks.extend(["Metal", "QuartzCore"])

        # Windows links with all libs by default
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(
                [
                    "kernel32",
                    "user32",
                    "gdi32",
                    "winmm",
                    "imm32",
                    "ole32",
                    "oleaut32",
                    "version",
                    "uuid",
                    "advapi32",
                    "setupapi",
                    "shell32",
                ]
            )
