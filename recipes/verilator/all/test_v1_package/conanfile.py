from conan.tools.apple import is_apple_os
from conans import ConanFile, CMake, tools
from conans.tools import Version
import os



class TestVerilatorConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    @property
    def _with_systemc_example(self):
        # systemc is not available on Macos
        if is_apple_os(self):
            return False
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "6":
            return False
        return True

    def requirements(self):
        if self._with_systemc_example:
            self.requires("systemc/2.3.4")

    def build(self):
        if not tools.cross_building(self.settings, skip_x64_x86=True):
            cmake = CMake(self)
            cmake.definitions["BUILD_SYSTEMC"] = self._with_systemc_example
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self.settings, skip_x64_x86=True):
            with tools.run_environment(self):
                self.run("perl {} --version".format(os.path.join(self.deps_cpp_info["verilator"].rootpath, "bin", "verilator")), run_environment=True)
            self.run(os.path.join("bin", "blinky"), run_environment=True)
            if self._with_systemc_example:
                self.run(os.path.join("bin", "blinky_sc"), run_environment=True)
