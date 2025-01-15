import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import Environment


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.tool_requires("cpython/<host_version>")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        if not can_run(self):
            tc.variables["Python_EXECUTABLE"] = os.path.join(self.dependencies.build["cpython"].package_folder, "bin", "python").replace("\\", "/")
        tc.generate()

        env = Environment()
        env.append_path("PYTHONPATH", os.path.join(self.build_folder, self.cpp.build.libdirs[0]))
        env.vars(self, scope="run").save_script("testrun")


    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            module_path = os.path.join(self.source_folder, "test.py")
            self.run(f'python "{module_path}"', env="conanrun")
