from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
import os


# It will become the standard on Conan 2.x
class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.settings.os == "Linux":
            tc.variables["WITH_X11"] = self.options["sdl"].x11
            tc.variables["WITH_ALSA"] = self.options["sdl"].alsa
            tc.variables["WITH_PULSE"] = self.options["sdl"].pulse
            tc.variables["WITH_ESD"] = self.options["sdl"].esd
            tc.variables["WITH_ARTS"] = self.options["sdl"].arts
            tc.variables["WITH_DIRECTFB"] = self.options["sdl"].directfb
        if self.settings.os == "Windows":
            tc.variables["WITH_DIRECTX"] = self.options["sdl"].directx
        tc.generate()


    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
