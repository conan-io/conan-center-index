from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
import os


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
        if self.settings.os == "Windows":
            self.run("ndk-build.cmd --version")
        else:
            self.run("ndk-build --version")

        # INFO: Run the project that was built using Android NDK
        if self.settings.os == "Android":
            test_file = os.path.join(self.cpp.build.bindirs[0], "test_package")
            assert os.path.exists(test_file)
