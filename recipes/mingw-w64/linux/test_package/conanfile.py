import os
from conans import ConanFile, tools


class MinGWTestConan(ConanFile):
    generators = "gcc"
    settings = "os", "arch", "compiler", "build_type"

    def build(self):
        source_file = os.path.join(self.source_folder, "main.cpp")
        self.run("x86_64-w64-mingw32-g++ {} @conanbuildinfo.gcc -lstdc++ -o main".format(source_file), run_environment=True)

    def test(self):
        if not tools.build.cross_building(self, self):
            self.run("x86_64-w64-mingw32-g++ --version", run_environment=True)
