from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration

import os


class IosCMakeConan(ConanFile):
    name = "ios-cmake"
    license = "BSD-3-Clause"
    settings = "os" , "arch"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/leetal/ios-cmake"
    options = {
        "enable_bitcode": [True, False],
        "enable_arc": [True, False],
        "enable_visibility": [True, False],
        "enable_strict_try_compile": [True, False],
        "toolchain_target": ["auto", "OS", "OS64", "OS64COMBINED",
                       "SIMULATOR", "SIMULATOR64", "SIMULATORARM64",
                       "TVOS", "TVOSCOMBINED",
                       "SIMULATOR_TVOS", "WATCHOS",
                       "WATCHOSCOMBINED", "SIMULATOR_WATCHOS",
                       "MAC", "MAC_ARM64", "MAC_CATALYST", "MAC_CATALYST_ARM64"]
    }
    default_options = {
        "enable_bitcode": True,
        "enable_arc": True,
        "enable_visibility": False,
        "enable_strict_try_compile": False,
        "toolchain_target": "auto",
    }
    description = "ios Cmake toolchain to (cross) compile macOS/iOS/watchOS/tvOS"
    topics = "conan", "apple", "ios", "cmake", "toolchain", "ios", "tvos", "watchos"
    exports_sources =  "cmake-wrapper"

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == 'posix':
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def configure(self):
        if not tools.apple.is_apple_os(self):
            raise ConanInvalidConfiguration("This package only supports Apple operating systems")

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
        raise ConanInvalidConfiguration("Can not guess toolchain_target. Please set the option explicit (or check our os settings)")


    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("ios-cmake-{}".format(self.version), self._source_subfolder)

    def build(self):
        pass # there is nothing to build

    def package(self):
        self.copy("cmake-wrapper", dst="bin")
        self.copy("ios.toolchain.cmake",
                    src=self._source_subfolder,
                    dst=os.path.join("lib", "cmake", "ios-cmake"),
                    keep_path=False)
        self._chmod_plus_x(os.path.join(self.package_folder, "bin", "cmake-wrapper"))

        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder, keep_path=False)
        # satisfy KB-H014 (header_only recipes require headers)
        tools.files.save(self, os.path.join(self.package_folder, "include", "dummy_header.h"), "\n")

    def package_info(self):
        if self.settings.os == "Macos":
            if not getattr(self, "settings_target", None):
                #  not a build_require , but can be fine since its build as a ppr:b, but nothing to do
                return
            # this is where I want to be, expecting this as a build_require for a host
            target_os = str(self.settings_target.os)
            arch_flag = self.settings_target.arch
            target_version= self.settings_target.os.version
        elif self.settings.os == "iOS": # old style 1 profile, don't use
            target_os = str(self.settings.os)
            arch_flag = self.settings.arch
            target_version = self.settings.os.version
        else:
            #hackingtosh ? hu
            raise ConanInvalidConfiguration("Building for iOS on a non Mac platform? Please tell me how!")

        if self.options.toolchain_target == "auto":
            toolchain_target = self._guess_toolchain_target(target_os, arch_flag)
        else:
            toolchain_target = self.options.toolchain_target


        if arch_flag == "armv8":
            arch_flag = "arm64"
        elif arch_flag == "armv8.3":
            arch_flag = "arm64e"

        cmake_options = "-DENABLE_BITCODE={} -DENABLE_ARC={} -DENABLE_VISIBILITY={} -DENABLE_STRICT_TRY_COMPILE={}".format(
            self.options.enable_bitcode,
            self.options.enable_arc,
            self.options.enable_visibility,
            self.options.enable_strict_try_compile
        )
        # Note that this, as long as we specify (overwrite) the ARCHS, PLATFORM has just limited effect,
        # but PLATFORM need to be set in the profile so it makes sense, see ios-cmake docs for more info
        cmake_flags = "-DPLATFORM={} -DDEPLOYMENT_TARGET={} -DARCHS={} {}".format(
            toolchain_target, target_version, arch_flag, cmake_options
        )

        self.env_info.CONAN_USER_CMAKE_FLAGS = cmake_flags
        self.output.info("Setting toolchain options to: {}".format(cmake_flags))
        cmake_wrapper = os.path.join(self.package_folder, "bin", "cmake-wrapper")
        self.output.info("Setting CONAN_CMAKE_PROGRAM to: {}".format(cmake_wrapper))
        self.env_info.CONAN_CMAKE_PROGRAM = cmake_wrapper
        tool_chain = os.path.join(self.package_folder,
                                    "lib",
                                    "cmake",
                                    "ios-cmake",
                                    "ios.toolchain.cmake")
        self.env_info.CONAN_CMAKE_TOOLCHAIN_FILE = tool_chain
        # add some more env_info, for the case users generate a toolchain file via conan and want to access that info
        self.env_info.CONAN_ENABLE_BITCODE_FLAG = str(self.options.enable_bitcode)
        self.env_info.CONAN_ENABLE_ARC_FLAG = str(self.options.enable_arc)
        self.env_info.CONAN_ENABLE_VISIBILITY_FLAG = str(self.options.enable_visibility)
        self.env_info.CONAN_ENABLE_STRICT_TRY_COMPILE_FLAG = str(self.options.enable_strict_try_compile)
        # the rest should be exported from profile info anyway

    def package_id(self):
        self.info.header_only()
        # TODO , since we have 2 profiles I am not sure that this is still required
        # since this will always be / has to be  a build profile
