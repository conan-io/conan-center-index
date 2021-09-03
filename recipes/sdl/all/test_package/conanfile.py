from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

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
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
