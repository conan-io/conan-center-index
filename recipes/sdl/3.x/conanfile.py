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
        **{subsystem: [None, True, False] for subsystem, _ in _subsystems},
        **{
            "alsa": [None, True, False],
        }
    }

    default_options = {
        **{
            "shared": False,
            "fPIC": False,
        },
        **{subsystem: None for subsystem, _ in _subsystems},
        **{
            "alsa": None,
        }
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

        # If the user has not explicitly set value to any of the subsystems, we should
        # - If they have deps, its default value is False
        # - Otherwise, they are True
        # See CMakeLists.txt#L220, but we #L1167 seems to indicate otherwise, so set them all to True
        for subsystem, dependencies in _subsystems:
            # Don't use is with get_safe, it does not return None, but a _PackageOption with a None value
            # Let the overridden equality check if the option is None
            if self.options.get_safe(subsystem) == None:
                default_subsystem_value = True
                if subsystem == "hidapi" and self.settings.os == "visionOS":
                    # CMakeLists.txt#L378
                    default_subsystem_value = False
                setattr(self.options, subsystem, default_subsystem_value)

        if self.options.get_safe("alsa") == None:
            # CMakeLists.txt#L298
            setattr(self.options, "alsa", self._is_unix_sys and self.options.get_safe("audio"))

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
        # TODO: Add option for opengl
        return (self.options.get_safe("video")
                and self.settings.os not in ("iOS", "tvOS", "watchOS"))

    @property
    def _supports_libudev(self):
        # CMakeLists.txt#L351&L1618
        # TODO: Add option for libudev
        return self.settings.os in ("Linux", "FreeBSD")

    @property
    def _supports_pulseaudio(self):
        # CMakeLists.txt#L372
        # TODO: Add option for pulseaudio
        return self._is_unix_sys and self.options.get_safe("audio")

    @property
    def _supports_dbus(self):
        # CMakeLists.txt#292
        # TODO: Add option for dbus
        return self._is_unix_sys

    def requirements(self):
        if self._needs_libusb:
            self.requires("libusb/1.0.26")
        if self._supports_opengl:
            self.requires("opengl/system")
        if self._supports_libudev:
            self.requires("libudev/system")
        if self._supports_dbus:
            self.requires("dbus/1.15.8")
        if self._supports_pulseaudio:
            self.requires("pulseaudio/17.0")
        if self.options.get_safe("alsa"):
            self.requires("libalsa/1.2.12")

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
        if self._needs_libusb:
            tc.cache_variables["SDL_HIDAPI_LIBUSB"] = True
            tc.cache_variables["SDL_HIDAPI_LIBUSB_SHARED"] = self.dependencies["libusb"].options.get_safe("shared", False)
        if self.options.get_safe("alsa"):
            tc.cache_variables["SDL_ALSA"] = True
            tc.cache_variables["SDL_ALSA_SHARED"] = self.dependencies["libalsa"].options.shared
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

    def package_info(self):
        self.cpp_info.libs = ["SDL3"]
        self.cpp_info.set_property("cmake_file_name", "SDL3")
        self.cpp_info.set_property("cmake_target_name", "SDL3::SDL3")
        # CMakeLists.txt#L120
        if self.settings.os in ("Linux", "FreeBSD", "Macos"):
            self.cpp_info.system_libs.append("pthread")

        # TODO: dl support in Unix/Macos, CMakeLists.txt#L1209
        # TODO: Android support of opengles if video is enabled, CMakeLists.txt#L1349

        # CMakeLists.txt#L327
        if self.settings.os == "Macos" and self.options.get_safe("video"):
            self.cpp_info.frameworks.append("Cocoa")
