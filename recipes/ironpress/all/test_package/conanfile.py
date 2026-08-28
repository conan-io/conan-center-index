from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
import os


class IronpressTestPackage(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            for executable in ("ironpress_c_consumer", "ironpress_cpp_consumer"):
                if self.settings.os == "Windows":
                    executable += ".exe"
                path = os.path.join(self.cpp.build.bindir, executable)
                self.run(path, env="conanrun")
