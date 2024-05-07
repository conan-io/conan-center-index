import io

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.verbose = 1
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            buffer = io.StringIO()
            self.run(f'{bin_path} "{os.path.join(self.cpp.build.bindir)}"', buffer, env="conanrun")
            print(buffer.getvalue())
            assert "I found your message! It was 'A secret text'! I am 1337! :^)" in buffer.getvalue()
