import os
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.build import cross_building as tools_cross_building
from conan.tools.layout import cmake_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"

    def requirements(self):
        self.requires("protobuf/3.21.1")
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.tool_requires("protobuf/3.21.1")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["GOOGLEAPIS_RES_DIR"] = self.dependencies["googleapis"].cpp_info.resdirs[0].replace("\\", "/")
        tc.generate()

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools_cross_building(self):
            self.run(os.path.join(self.cpp.build.bindirs[0], "test_package"), env="conanrun")
