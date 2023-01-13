from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualBuildEnv", "VirtualRunEnv"
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
        self.run("win_flex --version")
        self.run("win_bison --version")
        if not cross_building(self):
            bison_test = os.path.join(self.cpp.build.bindirs[0], "bison_test_package")
            self.run(bison_test, env="conanrun")
            flex_test = os.path.join(self.cpp.build.bindirs[0], "flex_test_package")
            basic_nr_txt = os.path.join(self.source_folder, "basic_nr.txt")
            self.run(f"{flex_test} {basic_nr_txt}", env="conanrun")
