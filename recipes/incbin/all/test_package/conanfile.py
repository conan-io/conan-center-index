from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
from conan.tools.microsoft import is_msvc
import os
from io import StringIO

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        if is_msvc(self) and can_run(self):
            stderr_capture = StringIO()
            self.run("incbin_tool", env="conanrun", stderr=stderr_capture, ignore_errors=True)
            assert "-help" in stderr_capture.getvalue()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
