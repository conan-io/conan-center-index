from conans import ConanFile, CMake, tools
import os


class TestVerilatorConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def requirements(self):
        self.requires("systemc/2.3.3")

    def build(self):
        if not tools.cross_building(self.settings, skip_x64_x86=True):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self.settings, skip_x64_x86=True):
            with tools.run_environment(self):
                self.run("perl {} --version".format(os.path.join(self.deps_cpp_info["verilator"].rootpath, "bin", "Verilator")), run_environment=True)
            self.run(os.path.join("bin", "blinky"), run_environment=True)
            if self.settings.compiler != "Visual Studio":
                # systemc does not run on MSVC: https://forums.accellera.org/topic/6621-systemc-233-using-msvc-causes-read-access-violation/
                self.run(os.path.join("bin", "blinky_sc"), run_environment=True)
