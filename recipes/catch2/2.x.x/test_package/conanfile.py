from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout
import os

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    _tests_todo = []

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["WITH_PREFIX"]    = self.dependencies[self.tested_reference_str].options.with_prefix
        tc.variables["WITH_MAIN"]      = self.dependencies[self.tested_reference_str].options.with_main
        tc.variables["WITH_BENCHMARK"] = self.dependencies[self.tested_reference_str].options.with_main and self.dependencies[self.tested_reference_str].options.with_benchmark
        tc.generate()

        # note: this is required as self.dependencies is not available in test()
        self._tests_todo.append("test_package")
        if self.dependencies[self.tested_reference_str].options.with_main:
            self._tests_todo.append("standalone")
            if self.dependencies[self.tested_reference_str].options.with_benchmark:
                self._tests_todo.append("benchmark")

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            for test_name in self._tests_todo:
                self.run(os.path.join(self.cpp.build.bindirs[0], test_name), env="conanrun")
