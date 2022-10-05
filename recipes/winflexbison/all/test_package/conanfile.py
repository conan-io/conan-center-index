from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualBuildEnv", "VirtualRunEnv"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            self.run("win_flex --version", env="conanbuild")
            self.run("win_bison --version", env="conanbuild")

            bison_test = os.path.join(self.cpp.build.bindirs[0], "bison_test_package")
            self.run(bison_test, env="conanrun")
            flex_test = os.path.join(self.cpp.build.bindirs[0], "flex_test_package")
            basic_nr_txt = os.path.join(self.source_folder, "basic_nr.txt")
            self.run(f"{flex_test} {basic_nr_txt}", env="conanrun")
