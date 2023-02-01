import os
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualBuildEnv"
    test_type = "explicit"

    # Can be used as a requirement and a tool.
    def requirements(self):
        self.requires(self.tested_reference_str)
    
    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            self.output.info(f"Running AppRun inside AppDir: {os.path.join(self.cpp.build.bindirs[0], 'AppDir', 'AppRun')}")
            self.run(os.path.join(self.cpp.build.bindirs[0], "AppDir", "AppRun"), run_environment=False)
