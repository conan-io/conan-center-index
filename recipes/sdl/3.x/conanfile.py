from conan import ConanFile
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
        }
    }

    default_options = {
        **{
            "shared": False,
            "fPIC": False,
        },
        **{subsystem: True for subsystem, _ in _subsystems},
        **{
            ## Audio
            # Linux only
            "alsa": False,
            "pulseaudio": False,
            "sndio": False,
            ## Video
            "opengl": True,  # TODO: Off by default in apple_os
            "opengles": True,
            ## Other
            "libudev": True,
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

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

        if not self.options.get_safe("audio"):
            self.options.rm_safe("alsa")
            self.options.rm_safe("pulseaudio")
            self.options.rm_safe("sndio")

        if not self.options.get_safe("video"):
            self.options.rm_safe("opengl")
            self.options.rm_safe("opengles")

    def validate(self):
        # If any of the subsystems is enabled, then the corresponding dependencies must be enabled
        for subsystem, dependencies in _subsystems:
            if self.options.get_safe(subsystem):
                for dependency in dependencies:
                    if not self.options.get_safe(dependency):
                        raise ConanInvalidConfiguration(f'-o="&:{subsystem}=True" subsystem requires -o="&:{dependency}=True"')

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
        # TODO: Add option for libusb
        return (self.options.get_safe("hidapi") and
                (not is_apple_os(self) or self.settings.os == "Macos") and
                self.settings.os != "Android")

    @property
    def _supports_opengl(self):
        # CMakeLists.txt#L297
        return (self.options.get_safe("opengl")
                and self.settings.os not in ("iOS", "tvOS", "watchOS"))

    @property
    def _supports_opengles(self):
        # CMakeLists.txt#L297
        return (self.options.get_safe("opengles")
                and self.settings.os not in ("iOS", "tvOS", "watchOS"))

    @property
    def _supports_libudev(self):
        # CMakeLists.txt#L351&L1618
        return (self.options.get_safe("libudev")
                and self.settings.os in ("Linux", "FreeBSD"))

    @property
    def _supports_dbus(self):
        # CMakeLists.txt#292
        # TODO: Add option for dbus
        return self._is_unix_sys

    def requirements(self):
        # TODO: understand if we want to make this an option
        self.requires("libiconv/1.17")
        if self._needs_libusb:
            self.requires("libusb/1.0.26")
        if self._supports_opengl:
            self.requires("opengl/system")
        if self._supports_libudev:
            self.requires("libudev/system")
        if self._supports_dbus:
            self.requires("dbus/1.15.8")
        if self.options.get_safe("pulseaudio"):
            self.requires("pulseaudio/17.0")
        if self.options.get_safe("alsa"):
            self.requires("libalsa/1.2.12")
        if self.options.get_safe("sndio"):
            self.requires("sndio/1.9.0")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.24 <4]")
        if self.settings.os == "Linux" and not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["SDL_SHARED"] = self.options.shared
        tc.cache_variables["SDL_STATIC"] = not self.options.shared
        # Todo: Remove after recipe develop is finished
        tc.cache_variables["SDL_TEST_LIBRARY"] = True
        tc.cache_variables["SDL_TESTS"] = True
        tc.cache_variables["SDL_EXAMPLES"] = True
        tc.cache_variables["CMAKE_TRY_COMPILE_CONFIGURATION"] = str(self.settings.build_type)
        tc.cache_variables["SDL_SYSTEM_ICONV_DEFAULT"] = True
        tc.cache_variables["SDL_LIBICONV"] = True
        if self._supports_opengl:
            tc.cache_variables["SDL_OPENGL"] = True
        if self._supports_opengles:
            tc.cache_variables["SDL_OPENGLES"] = True
        if self._needs_libusb:
            tc.cache_variables["SDL_HIDAPI_LIBUSB"] = True
            tc.cache_variables["SDL_HIDAPI_LIBUSB_SHARED"] = self.dependencies["libusb"].options.get_safe("shared", False)
        if self.options.get_safe("pulseaudio"):
            tc.cache_variables["SDL_PULSEAUDIO"] = True
            tc.cache_variables["SDL_PULSEAUDIO_SHARED"] = self.dependencies["pulseaudio"].options.get_safe("shared", True)
        if self.options.get_safe("alsa"):
            tc.cache_variables["SDL_ALSA"] = True
            tc.cache_variables["SDL_ALSA_SHARED"] = self.dependencies["libalsa"].options.shared
        if self.options.get_safe("sndio"):
            tc.cache_variables["SDL_SNDIO"] = True
            tc.cache_variables["SDL_SNDIO_SHARED"] = True  # sndio is always shared
        tc.cache_variables["SDL_LIBUDEV"] = self._supports_libudev
        tc.generate()
        deps = CMakeDeps(self)
        deps.set_property("libusb", "cmake_target_name", "LibUSB::LibUSB")
        deps.set_property("libusb", "cmake_additional_variables_prefixes", ["LibUSB"])
        deps.generate()
        pcdeps = PkgConfigDeps(self)
        pcdeps.generate()


    def build(self):
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

        # TODO: Link opengles
        #             if self.options.opengles:
        #                 self.cpp_info.components["libsdl2"].system_libs.extend(["GLESv1_CM", "GLESv2"])
        #                 self.cpp_info.components["libsdl2"].system_libs.append("OpenSLES")

        # CMakeLists.txt#L327
        if self.settings.os == "Macos" and self.options.get_safe("video"):
            self.cpp_info.frameworks.append("Cocoa")
