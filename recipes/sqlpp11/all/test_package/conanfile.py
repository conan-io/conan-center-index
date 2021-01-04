from conans import ConanFile, CMake, tools
import os


class Sqlpp11TestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        exe_name = "example"
        if tools.cross_building(self.settings) and not tools.os_info.is_windows:
            if self.settings.os == "Emscripten":
                exe_name = "example.js"
            elif self.settings.os == "Windows":
                exe_name = "example.exe"
            assert(os.path.exists(os.path.join("bin", exe_name)))
        else:
            self.run(os.path.join("bin", "example"), run_environment=True)
