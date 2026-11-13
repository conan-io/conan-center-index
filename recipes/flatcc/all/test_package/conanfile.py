from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str, run=True)

    def test(self):
        if can_run(self) and not self.dependencies[self.tested_reference_str].options.runtime_lib_only:
            self.run("flatcc --version", env="conanrun")
