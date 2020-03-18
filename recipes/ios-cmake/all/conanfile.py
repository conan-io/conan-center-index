
from conans import ConanFile, tools

import os
import platform
import copy


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
        "ios_target": ["OS", "OS64", "OS64COMBINED",
                       "SIMULATOR", "SIMULATOR64",
                       "TVOS", "TVOSCOMBINED",
                       "SIMULATOR_TVOS", "WATCHOS",
                       "WATCHOSCOMBINED", "SIMULATOR_WATCHOS"]
    }
    default_options = {
        "enable_bitcode": False,
        "enable_arc": False,
        "enable_visibility": False,
        "enable_strict_try_compile": False,
        "ios_target": "OS64COMBINED", 
    }
    description = "ios Cmake toolchain to (cross) compile macOS/iOS/watchOS/tvOS"
    url = "https://github.com/leetal/ios-cmake"
    exports_sources =  "cmake-wrapper"

    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == 'posix':
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("ios-cmake-{}".format(self.version), self._source_subfolder())

    def build(self):
        pass # there is nothign to build

    def package(self):
        self.copy("cmake-wrapper")
        self.copy("ios.toolchain.cmake", src=self._source_subfolder(),  dst="ios-cmake", keep_path=False)

    def package_info(self):

        arch_flag = self.settings.arch
        if arch_flag == "armv8":
            arch_flag = "arm64"

        cmake_options = "-DENABLE_BITCODE={} -DENABLE_ARC={} -DENABLE_VISIBILITY={} -DENABLE_STRICT_TRY_COMPILE={}".format(
            self.options.enable_bitcode, 
            self.options.enable_arc, 
            self.options.enable_visibility,
            self.options.enable_strict_try_compile  
        ) 
        # Note that this, as long as we specify (overwrite) the ARCHS, PLATFORM has just limited effect, 
        # but PLATFORM need to be set in the profile so it makes sense, see ios-cmake docs for more info
        cmake_flags = "-DPLATFORM={} -DDEPLOYMENT_TARGET={} -DARCHS={} {}".format(
            self.options.ios_target, self.settings.os.version, arch_flag, cmake_options
        ) 

        self.cpp_info.builddirs = ["ios-cmake"]

        self.env_info.CONAN_USER_CMAKE_FLAGS = cmake_flags
        self.output.info('Setting toolchain options to: %s' % cmake_flags)
        cmake_wrapper = os.path.join(self.package_folder, "cmake-wrapper")
        self._chmod_plus_x(cmake_wrapper)
        self.output.info('Setting CONAN_CMAKE_PROGRAM to: %s' % cmake_wrapper)
        self.env_info.CONAN_CMAKE_PROGRAM = cmake_wrapper
        tool_chain = os.path.join(self.package_folder,
                                  "ios-cmake",
                                  "ios.toolchain.cmake"
                                  )
        self.env_info.CONAN_CMAKE_TOOLCHAIN_FILE = tool_chain

    def package_id(self):
        self.info.header_only()
