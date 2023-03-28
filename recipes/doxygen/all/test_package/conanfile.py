from conan import ConanFile
from conan.tools.cmake import cmake_layout, CMake
from conan.errors import ConanException
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualBuildEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not os.path.isdir(os.path.join(self.build_folder, "html")):
            raise ConanException("doxygen did not create html documentation directory")

        self.output.info("Version:")
        self.run("doxygen --version")
