from conan import ConanFile, tools
from conan.tools.build import cross_building
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def test(self):
        def chmod_plus_x(name):
            if os.name == 'posix':
                os.chmod(name, os.stat(name).st_mode | 0o111)

        cc = os.environ["CC"]
        cxx = os.environ["CXX"]
        hello_c = os.path.join(self.source_folder, "hello.c")
        hello_cpp = os.path.join(self.source_folder, "hello.cpp")
        self.run("%s --version" % cc, run_environment=True)
        self.run("%s --version" % cxx, run_environment=True)
        self.run("%s -dumpversion" % cc, run_environment=True)
        self.run("%s -dumpversion" % cxx, run_environment=True)
        self.run("%s %s -o hello_c" % (cc, hello_c), run_environment=True)
        self.run("%s %s -o hello_cpp" % (cxx, hello_cpp), run_environment=True)
        if not cross_building(self):
            chmod_plus_x("hello_c")
            chmod_plus_x("hello_cpp")
            self.run("./hello_c", run_environment=True)
            self.run("./hello_cpp", run_environment=True)
        if tools.which("readelf"):
            self.run("readelf -l hello_c", run_environment=True)
            self.run("readelf -l hello_cpp", run_environment=True)
        if tools.which("otool"):
            self.run("otool -L hello_c", run_environment=True)
            self.run("otool -L hello_cpp", run_environment=True)
