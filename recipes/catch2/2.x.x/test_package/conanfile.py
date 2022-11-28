from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout
import os
import yaml

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    _tests_todo = []

    @property
    def _todos_filename(self):
        return os.path.join(self.recipe_folder, self.folders.generators, "catch2_test_to_do.yml")

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        tc = CMakeToolchain(self)
        catch_opts = self.dependencies[self.tested_reference_str].options
        tc.variables["WITH_PREFIX"]    = catch_opts.with_prefix
        tc.variables["WITH_MAIN"]      = catch_opts.with_main
        tc.variables["WITH_BENCHMARK"] = not catch_opts.with_prefix and catch_opts.with_main and catch_opts.with_benchmark
        tc.generate()

        # note: this is required as self.dependencies is not available in test()
        self._tests_todo.append("test_package")
        if catch_opts.with_main:
            self._tests_todo.append("standalone")
        if not catch_opts.with_prefix and catch_opts.with_main and catch_opts.with_benchmark:
            self._tests_todo.append("benchmark")

        with open(self._todos_filename, "w", encoding="utf-8") as file:
            yaml.dump(self._tests_todo, file)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        with open(self._todos_filename, "r", encoding="utf-8") as file:
            self._tests_todo = yaml.safe_load(file)
        if can_run(self):
            for test_name in self._tests_todo:
                self.run(os.path.join(self.cpp.build.bindirs[0], test_name), env="conanrun")
