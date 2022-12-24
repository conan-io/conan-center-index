from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
import os


# It will become the standard on Conan 2.x
class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        if self.settings.os == "Linux":
            cmake.definitions["WITH_X11"] = self.options["sdl"].x11
            cmake.definitions["WITH_ALSA"] = self.options["sdl"].alsa
            cmake.definitions["WITH_PULSE"] = self.options["sdl"].pulse
            cmake.definitions["WITH_ESD"] = self.options["sdl"].esd
            cmake.definitions["WITH_ARTS"] = self.options["sdl"].arts
            cmake.definitions["WITH_DIRECTFB"] = self.options["sdl"].directfb
        if self.settings.os == "Windows":
            cmake.definitions["WITH_DIRECTX"] = self.options["sdl"].directx
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
