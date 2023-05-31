import os
from conan import ConanFile
from conan.tools.build import can_run


class MinGWTestConan(ConanFile):
    generators = "gcc"
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def build(self):
        source_file = os.path.join(self.source_folder, "main.cpp")
        self.run("gcc.exe {} @conanbuildinfo.gcc -lstdc++ -o main".format(source_file))

    def test(self):
        self.run("gcc.exe --version")
        if can_run(self):
            self.run("main")
