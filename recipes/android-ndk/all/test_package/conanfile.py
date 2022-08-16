import os
from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.build import cross_building


class TestPackgeConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualRunEnv"

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
        if not cross_building(self):
            if self.settings.os == "Windows":
                self.run("ndk-build.cmd --version", env="conanrun")
            else:
                self.run("ndk-build --version", env="conanrun")

        # INFO: Run the project that was built using Android NDK
        if self.settings.os == "Android":
            test_file = os.path.join("bin", "test_package")
            assert os.path.exists(test_file)
