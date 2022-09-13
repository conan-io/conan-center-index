from conan import ConanFile
from conan.tools.cmake import CMake
from conan.tools.build import can_run

import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            self.run("test_package", run_environment=True, env="conanrun")
            tclsh = self.deps_user_info['tcl'].tclsh
            assert(os.path.exists(tclsh))
            self.run("{} {}".format(tclsh, os.path.join(self.source_folder, "hello.tcl")), run_environment=True, env="conanrun")
