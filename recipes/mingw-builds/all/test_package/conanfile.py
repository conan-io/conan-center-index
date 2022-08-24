import os
from conans import ConanFile, tools


class MinGWTestConan(ConanFile):
    generators = "gcc"
    settings = "os", "arch", "compiler", "build_type"

    def build(self):
        source_file = os.path.join(self.source_folder, "main.cpp")
        self.run("gcc.exe {} @conanbuildinfo.gcc -lstdc++ -o main".format(source_file), run_environment=True)

    def test(self):
        if not tools.build.cross_building(self, self):
            self.run("gcc.exe --version", run_environment=True)
            self.run("main")
