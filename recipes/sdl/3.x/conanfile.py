from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, replace_in_file, rm, rmdir, copy
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import Environment

import os

required_conan_version = ">=1.55.0"

# Subsystems, CMakeLists.txt#L234
_subsystems = [
    ("audio",),
    ("video",),
    ("gpu", ["video"]),
    ("render", ["video"]),
    ("camera", ["video"]),
    ("joystick",),
    ("haptic", ["joystick"]),
    ("hidapi",),
    ("power",),
    ("sensor",),
    ("dialog",),
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
        **{subsystem: [None, True, False] for subsystem, _ in _subsystems}
    }

    default_options = {
        **{
            "shared": False,
            "fPIC": False,
        },
        **{subsystem: None for subsystem, _ in _subsystems}
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
                # self.options[subsystem] = not dependencies
                self.options[subsystem] = True

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

    def requirements(self):
        pass

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.24 <4]")
        if self.settings.os == "Linux" and not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SDL_SHARED"] = self.options.shared
        tc.variables["SDL_STATIC"] = not self.options.shared
        # Todo: Remove after recipe develop is finished
        tc.variables["SDL_TEST_LIBRARY"] = True
        tc.variables["SDL_TESTS"] = True
        tc.variables["SDL_EXAMPLES"] = True
        tc.generate()

    def package_info(self):
        # CMakeLists.txt#L120
        if self.settings.os in ("Linux", "FreeBSD", "Macos"):
            self.cpp_info.system_libs.append("pthread")

        # TODO: dl support in Unix/Macos, CMakeLists.txt#L1209
        # TODO: Android support of opengles if video is enabled, CMakeLists.txt#L1349

