from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.layout import basic_layout


class TzTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "VirtualBuildEnv", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        basic_layout(self)

    def test(self):
        if can_run(self):
            self.run('zdump -v America/Los_Angeles', env="conanrun")
