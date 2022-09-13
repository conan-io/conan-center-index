from pathlib import Path

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake


class TclTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            self.run(self.build_path.joinpath("test_package"), run_environment=True, env="conanrun")

            tclsh = self.deps_user_info['tcl'].tclsh
            assert(Path(tclsh).exists())
            self.run(f"{tclsh} {self.source_path.joinpath('hello.tcl')}", run_environment=True, env="conanrun")
