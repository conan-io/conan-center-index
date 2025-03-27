from conan import ConanFile
from conan.tools.cmake import cmake_layout
from conan.tools.build import can_run


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def test(self):
        if can_run(self):
            self.run("kcov --version", env="conanrun")
