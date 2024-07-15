import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.files import copy, get, save
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class IosCMakeConan(ConanFile):
    name = "ios-cmake"
    description = "iOS CMake toolchain to (cross) compile macOS/iOS/watchOS/tvOS"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/leetal/ios-cmake"
    topics = ("apple", "ios", "cmake", "toolchain", "ios", "tvos", "watchos", "header-only")

    package_type = "build-scripts"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "enable_bitcode": [True, False],
        "enable_arc": [True, False],
        "enable_visibility": [True, False],
        "enable_strict_try_compile": [True, False],
        "toolchain_target": [
            "auto",
            "OS",
            "OS64",
            "OS64COMBINED",
            "SIMULATOR",
            "SIMULATOR64",
            "SIMULATORARM64",
            "TVOS",
            "TVOSCOMBINED",
            "SIMULATOR_TVOS",
            "WATCHOS",
            "WATCHOSCOMBINED",
            "SIMULATOR_WATCHOS",
            "MAC",
            "MAC_ARM64",
            "MAC_CATALYST",
            "MAC_CATALYST_ARM64",
        ],
    }
    default_options = {
        "enable_bitcode": True,
        "enable_arc": True,
        "enable_visibility": False,
        "enable_strict_try_compile": False,
        "toolchain_target": "auto",
    }

    def export_sources(self):
        copy(self, "cmake-wrapper", self.recipe_folder, self.export_sources_folder)

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if not is_apple_os(self):
            raise ConanInvalidConfiguration("This package only supports Apple operating systems")

    def package_id(self):
        self.info.clear()

    def _guess_toolchain_target(self, os, arch):
        if os == "iOS":
            if arch in ["armv8", "armv8.3"]:
                return "OS64"
            if arch == "x86_64":
                return "SIMULATOR64"
            # 32bit is dead, don't care
        elif os == "watchOS":
            if arch == "x86_64":
                return "SIMULATOR_WATCHOS"
            else:
                return "WATCHOS"
        elif os == "tvOS":
            if arch == "x86_64":
                return "TVOS"
            else:
                return "SIMULATOR_TVOS"
        raise ConanInvalidConfiguration(
            "Cannot guess toolchain_target. "
            "Please set the option explicitly (or check your os settings)."
        )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass  # there is nothing to build

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == "posix":
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def package(self):
        copy(self, "cmake-wrapper",
             src=self.export_sources_folder,
             dst=os.path.join(self.package_folder, "bin"))
        copy(self, "ios.toolchain.cmake",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "lib", "cmake", "ios-cmake"),
             keep_path=False)
        self._chmod_plus_x(os.path.join(self.package_folder, "bin", "cmake-wrapper"))

        copy(self, "LICENSE.md",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder,
             keep_path=False)
        # satisfy KB-H014 (header_only recipes require headers)
        save(self, os.path.join(self.package_folder, "include", "dummy_header.h"), "\n")

    @property
    def _platform_info(self):
        if is_apple_os(self):
            if not getattr(self, "settings_target", None):
                #  not a build_require, but can be fine since its build as a ppr:b, but nothing to do
                return None, None, None
            # this is where I want to be, expecting this as a build_require for a host
            target_os = str(self.settings_target.os)
            arch_flag = self.settings_target.arch
            target_version = self.settings_target.os.version
        elif self.settings.os == "iOS":  # old-style v1 profile, don't use
            target_os = str(self.settings.os)
            arch_flag = self.settings.arch
            target_version = self.settings.os.version
        else:
            # hackingtosh ? hu
            raise ConanInvalidConfiguration("Building for iOS on a non-Mac platform? Please tell me how!")

        return target_os, arch_flag, target_version

    def package_info(self):
        target_os, arch_flag, target_version = self._platform_info
        if not target_os:
            return

        if self.options.toolchain_target == "auto":
            toolchain_target = self._guess_toolchain_target(target_os, arch_flag)
        else:
            toolchain_target = self.options.toolchain_target

        if arch_flag == "armv8":
            arch_flag = "arm64"
        elif arch_flag == "armv8.3":
            arch_flag = "arm64e"

        cmake_options = (
            f"-DENABLE_BITCODE={self.options.enable_bitcode} "
            f"-DENABLE_ARC={self.options.enable_arc} "
            f"-DENABLE_VISIBILITY={self.options.enable_visibility} "
            f"-DENABLE_STRICT_TRY_COMPILE={self.options.enable_strict_try_compile}"
        )
        # Note that this, as long as we specify (overwrite) the ARCHS, PLATFORM has just limited effect,
        # but PLATFORM need to be set in the profile so it makes sense, see ios-cmake docs for more info
        cmake_flags = (
            f"-DPLATFORM={toolchain_target} "
            f"-DDEPLOYMENT_TARGET={target_version} "
            f"-DARCHS={arch_flag} "
            f"{cmake_options}"
        )
        self.output.info(f"Setting toolchain options to: {cmake_flags}")
        cmake_wrapper = os.path.join(self.package_folder, "bin", "cmake-wrapper")
        self.output.info(f"Setting cmake-wrapper path to: {cmake_wrapper}")
        toolchain = os.path.join(self.package_folder, "lib", "cmake", "ios-cmake", "ios.toolchain.cmake")

        self.conf_info.define_path("user.ios-cmake:cmake_program", cmake_wrapper)
        self.conf_info.define_path("user.ios-cmake:cmake_toolchain_file", toolchain)
        self.conf_info.define("user.ios-cmake:cmake_flags", cmake_flags)
        self.conf_info.define("user.ios-cmake:enable_bitcode", bool(self.options.enable_bitcode))
        self.conf_info.define("user.ios-cmake:enable_arc", bool(self.options.enable_arc))
        self.conf_info.define("user.ios-cmake:enable_visibility", bool(self.options.enable_visibility))

        self.buildenv_info.define("CONAN_CMAKE_PROGRAM", cmake_wrapper)
        self.buildenv_info.define("CONAN_CMAKE_TOOLCHAIN_FILE", toolchain)
        self.buildenv_info.define("CONAN_USER_CMAKE_FLAGS", cmake_flags)
        # add some more env_info, for the case users generate a toolchain file via conan and want to access that info
        self.buildenv_info.define("CONAN_ENABLE_BITCODE_FLAG", str(self.options.enable_bitcode))
        self.buildenv_info.define("CONAN_ENABLE_ARC_FLAG", str(self.options.enable_arc))
        self.buildenv_info.define("CONAN_ENABLE_VISIBILITY_FLAG", str(self.options.enable_visibility))
        self.buildenv_info.define("CONAN_ENABLE_STRICT_TRY_COMPILE_FLAG", str(self.options.enable_strict_try_compile))
        # the rest should be exported from profile info anyway

        # TODO: Legacy, remove in Conan 2.0
        self.env_info.CONAN_USER_CMAKE_FLAGS = cmake_flags
        self.env_info.CONAN_CMAKE_PROGRAM = cmake_wrapper
        self.env_info.CONAN_CMAKE_TOOLCHAIN_FILE = toolchain
        self.env_info.CONAN_ENABLE_BITCODE_FLAG = str(self.options.enable_bitcode)
        self.env_info.CONAN_ENABLE_ARC_FLAG = str(self.options.enable_arc)
        self.env_info.CONAN_ENABLE_VISIBILITY_FLAG = str(self.options.enable_visibility)
        self.env_info.CONAN_ENABLE_STRICT_TRY_COMPILE_FLAG = str(self.options.enable_strict_try_compile)
