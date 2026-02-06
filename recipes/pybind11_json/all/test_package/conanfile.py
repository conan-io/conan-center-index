from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        # shared=True is both required on Windows, and a recommended default.
        # Recommended as a way for FindPython to work, see: https://github.com/conan-io/conan-center-index/issues/23151#issuecomment-2023141899
        self.tool_requires("cpython/[>=3.7]", options={"shared": True})
        # Required for test() below to find shared libraries.
        self.test_requires("cpython/[>=3.7]", options={"shared": True})

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
