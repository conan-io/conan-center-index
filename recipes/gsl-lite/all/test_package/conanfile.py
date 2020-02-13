from conans import ConanFile, CMake, tools
import os


class Gsl_liteTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if tools.cross_building(self.settings):
            if self.settings.os == "Emscripten":
                exe_name = "example.js"
            elif tools.os_info.is_windows:
                exe_name = "example.exe"
            else:
                exe_name = "example"
            assert(os.path.exists(os.path.join("bin", exe_name)))
        else:
            self.run(".%sexample" % os.sep, cwd="bin")
