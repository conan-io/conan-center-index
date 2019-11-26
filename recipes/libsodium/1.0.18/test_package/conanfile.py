from conans import ConanFile, CMake, tools
import os


class PackageTest(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if tools.cross_building(self.settings):
            if self.settings.os == "Emscripten":
                exe_name = "example.js"
            elif self.settings.os == "Windows":
                exe_name = "example.exe"
            else:
                exe_name = "example"
            assert(os.path.exists(os.path.join("bin", exe_name)))
        else:
            self.run(os.path.join("bin", "example"), run_environment=True)
