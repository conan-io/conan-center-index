import os
from conans import ConanFile, tools


class MinGWTestConan(ConanFile):
    generators = "gcc"
    settings = "os", "arch", "compiler", "build_type"

    def build(self):
        if self.settings.os == "Windows":
            source_file = os.path.join(self.source_folder, "main_windows.cpp")
            self.run("gcc.exe {} @conanbuildinfo.gcc -lstdc++ -o main".format(source_file), run_environment=True)
        else:
            source_file = os.path.join(self.source_folder, "main_linux.cpp")
            self.run("x86_64-w64-mingw32-g++ {} @conanbuildinfo.gcc -lstdc++ -o main".format(source_file), run_environment=True)

    def test(self):
        if not tools.cross_building(self):
            if self.settings.os == "Windows":
                self.run("gcc.exe --version", run_environment=True)
                self.run("main")
            else:
                self.run("x86_64-w64-mingw32-g++ --version", run_environment=True)
