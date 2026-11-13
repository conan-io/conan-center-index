from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain, CMakeDeps
from conan.tools.env import VirtualRunEnv


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str, visible=False, run=True)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_PROGRAM_PATH"] = self.dependencies[self.tested_reference_str].cpp_info.bindirs[0]
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        if can_run(self):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if can_run(self):
            self.run("swig -version", env="conanrun")
            self.run("swig -swiglib", env="conanrun")
