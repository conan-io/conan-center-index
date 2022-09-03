from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.settings.os == "Linux":
            tc.variables["WITH_X11"] = self.dependencies["sdl"].options.x11
            tc.variables["WITH_ALSA"] = self.dependencies["sdl"].options.alsa
            tc.variables["WITH_PULSE"] = self.dependencies["sdl"].options.pulse
            tc.variables["WITH_ESD"] = self.dependencies["sdl"].options.esd
            tc.variables["WITH_ARTS"] = self.dependencies["sdl"].options.arts
            tc.variables["WITH_DIRECTFB"] = self.dependencies["sdl"].options.directfb
        if self.settings.os == "Windows":
            tc.variables["WITH_DIRECTX"] = self.dependencies["sdl"].options.directx
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
