from conans import ConanFile, CMake, tools
import os


class TestVerilatorConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    @property
    def _build_systemc_example(self):
        # systemc is not available on Macos
        return self.settings.os != "Macos"

    @property
    def _run_systemc_example(self):
        # systemc does not run on MSVC: https://forums.accellera.org/topic/6621-systemc-233-using-msvc-causes-read-access-violation/
        return self._build_systemc_example and self.settings.compiler != "Visual Studio"

    def requirements(self):
        if self._build_systemc_example:
            self.requires("systemc/2.3.3")

    def build(self):
        if not tools.cross_building(self.settings, skip_x64_x86=True):
            cmake = CMake(self)
            cmake.definitions["BUILD_SYSTEMC"] = self._build_systemc_example
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self.settings, skip_x64_x86=True):
            with tools.run_environment(self):
                self.run("perl {} --version".format(os.path.join(self.deps_cpp_info["verilator"].rootpath, "bin", "verilator")), run_environment=True)
            self.run(os.path.join("bin", "blinky"), run_environment=True)
            if self._run_systemc_example:
                self.run(os.path.join("bin", "blinky_sc"), run_environment=True)
