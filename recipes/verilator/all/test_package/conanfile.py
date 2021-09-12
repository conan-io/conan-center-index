from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package"

    @property
    def _with_systemc_example(self):
        # systemc is not available on Macos
        return self.settings.os != "Macos"

    def requirements(self):
        if self._with_systemc_example:
            self.requires("systemc/2.3.3")

    def build(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            with tools.run_environment(self):
                with tools.environment_append({"VERILATOR_ROOT": self.deps_user_info["verilator"].verilator_root}):
                    cmake = CMake(self)
                    cmake.definitions["BUILD_SYSTEMC"] = self._with_systemc_example
                    cmake.configure()
                    cmake.build()

    def test(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            with tools.run_environment(self):
                self.run("perl {} --version".format(os.path.join(self.deps_cpp_info["verilator"].rootpath, "bin", "verilator")), run_environment=True)
            self.run(os.path.join("bin", "blinky"), run_environment=True)
            if self._with_systemc_example:
                self.run(os.path.join("bin", "blinky_sc"), run_environment=True)
