from conan import ConanFile, tools
from conan.tools.cmake import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        exe_name = "test_package"
        if self.settings.os == "Emscripten":
            exe_name += ".js"
        elif tools.os_info.is_windows:
            exe_name += ".exe"
        exec_path = os.path.join("bin", exe_name)
        if tools.cross_building(self.settings):
            assert(os.path.exists(exec_path))
        else:
            self.run(exec_path, run_environment=True)
