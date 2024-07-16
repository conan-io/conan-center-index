import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.files import copy, get
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
    # Note: you need to use `-o:b ...` to set these options due to package_type
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

    def config_options(self):
        if os.getenv("CONAN_CENTER_BUILD_SERVICE") is not None:
            # To not simply skip the build in C3I due to a missing toolchain_target value
            self.options.toolchain_target = "OS64"

    @property
    def _default_toolchain_target(self):
        if self.settings.os == "iOS":
            if self.settings.arch in ["armv8", "armv8.3"]:
                return "OS64"
            if self.settings.arch == "x86_64":
                return "SIMULATOR64"
            # 32bit is dead, don't care
        elif self.settings.os == "watchOS":
            if self.settings.arch == "x86_64":
                return "SIMULATOR_WATCHOS"
            else:
                return "WATCHOS"
        elif self.settings.os == "tvOS":
            if self.settings.arch == "x86_64":
                return "TVOS"
            else:
                return "SIMULATOR_TVOS"
        return None

    @property
    def _toolchain_target(self):
        if self.options.toolchain_target == "auto":
            return self._default_toolchain_target
        return self.options.toolchain_target

    def export_sources(self):
        copy(self, "cmake-wrapper", self.recipe_folder, self.export_sources_folder)

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if not is_apple_os(self):
            raise ConanInvalidConfiguration("This package only supports Apple operating systems")
        if self._toolchain_target is None:
            raise ConanInvalidConfiguration(
                "Cannot guess toolchain target type. "
                f"Please set the option explicitly with '-o:b {self.name}/*:toolchain_target=...'."
            )

    def package_id(self):
        self.info.clear()

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

    def package_info(self):
        settings = getattr(self, "settings_target", self.settings)

        if not settings.os:
            return

        arch_flag = str(settings.arch)
        if arch_flag == "armv8":
            arch_flag = "arm64"
        elif arch_flag == "armv8.3":
            arch_flag = "arm64e"

        cmake_options = " ".join([
            f"-DENABLE_BITCODE={self.options.enable_bitcode}",
            f"-DENABLE_ARC={self.options.enable_arc}",
            f"-DENABLE_VISIBILITY={self.options.enable_visibility}",
            f"-DENABLE_STRICT_TRY_COMPILE={self.options.enable_strict_try_compile}"
        ])
        # Note that this, as long as we specify (overwrite) the ARCHS, PLATFORM has just limited effect,
        # but PLATFORM need to be set in the profile so it makes sense, see ios-cmake docs for more info
        cmake_flags = " ".join([
            f"-DPLATFORM={self._toolchain_target}",
            f"-DDEPLOYMENT_TARGET={str(settings.os.version)}",
            f"-DARCHS={arch_flag}",
            f"{cmake_options}",
        ])
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
