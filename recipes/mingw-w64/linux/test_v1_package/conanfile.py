import os
from conan import ConanFile
from conan.tools.build import cross_building


class MinGWTestConan(ConanFile):
    generators = "gcc"
    settings = "os", "arch", "compiler", "build_type"

    def build(self):
        source_file = os.path.join(self.source_folder, os.pardir, "test_package", "main.cpp")
        self.run(f"x86_64-w64-mingw32-g++ {source_file} @conanbuildinfo.gcc -lstdc++ -o main", run_environment=True)

    def test(self):
        if not cross_building(self):
            self.run("x86_64-w64-mingw32-g++ --version", run_environment=True)
