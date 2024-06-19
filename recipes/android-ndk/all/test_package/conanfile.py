from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.scm import Version
import os
import platform


class TestPackgeConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "VirtualBuildEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        # INFO: It only makes sense to build a library, if the target OS is Android
        if self.settings.os == "Android":
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        ndk_build = "ndk-build.cmd" if self.settings.os == "Windows" else "ndk-build"
        ndk_version = Version(self.tested_reference_str.split('/')[1])
        skip_run = platform.system() == "Darwin" and "arm" in platform.processor() and ndk_version < "r23c"
        if not skip_run:
            self.run(f"{ndk_build} --version", env="conanbuild")
        else:
            self.output.warning("Skipped running ndk-build on macOS Apple Silicon in arm64 mode, please use a newer"
                                 " version of the Android NDK")

        # INFO: Run the project that was built using Android NDK
        if self.settings.os == "Android":
            test_file = os.path.join(self.cpp.build.bindirs[0], "test_package")
            assert os.path.exists(test_file)
