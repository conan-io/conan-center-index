import os
from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
import yaml


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    _tests_todo = []

    @property
    def _todos_filename(self):
        return os.path.join(self.recipe_folder, self.folders.generators, "soxr_test_to_do.yml")

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        # note: this is required as self.dependencies is not available in test()
        self._tests_todo.append("test_package_core")
        if self.dependencies[self.tested_reference_str].options.with_lsr_bindings:
            self._tests_todo.append("test_package_lsr")

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
