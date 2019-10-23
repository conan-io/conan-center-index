from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        self.build_cmake()

    def build_cmake(self):
        cmake = CMake(self)
        if self.settings.os == "Linux":
            cmake.definitions['WITH_X11'] = self.options['sdl2'].x11
            cmake.definitions['WITH_ALSA'] = self.options['sdl2'].alsa
            cmake.definitions['WITH_PULSE'] = self.options['sdl2'].pulse
            cmake.definitions['WITH_ESD'] = self.options['sdl2'].esd
            cmake.definitions['WITH_ARTS'] = self.options['sdl2'].arts
            cmake.definitions['WITH_DIRECTFB'] = self.options['sdl2'].directfb
        if self.settings.os == "Windows":
            cmake.definitions['WITH_DIRECTX'] = self.options['sdl2'].directx
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
