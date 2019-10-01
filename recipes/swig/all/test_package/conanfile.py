from conans import CMake, ConanFile, tools
from conans.errors import ConanException
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    # # FIXME: cpython is not available on CCI (yet)
    # def build(self):
    #     cmake = CMake(self)
    #     cmake.configure(args=["--trace", "--trace-expand"])
    #     cmake.build()
    #
    # def build_requirements(self):
    #     self.build_requires("cpython/3.8.3")
    #
    # def requirements(self):
    #     self.requires("cpython/3.8.3")

    def test(self):
        if not tools.cross_building(self.settings):
            # # FIXME: cpython is not available on CCI (yet)
            # with tools.chdir("lib"):
            #     self.run("python -c \"import sys; import _PackageTest; gcd = _PackageTest.gcd(12, 16); print('gcd =', gcd); sys.exit(0 if gcd == 4 else 1)\"", run_environment=True)
            #     self.run("python -c \"import sys; import _PackageTest; foo = _PackageTest.cvar.foo; print('foo =', foo); sys.exit(0 if foo == 3.14159265359 else 1)\"", run_environment=True)
            testdir = os.path.dirname(os.path.realpath(__file__))
            self.run("swig -python -outcurrentdir %s" % os.path.join(testdir, "test.i"))
            if not os.path.isfile("example.py"):
                raise ConanException("example.py is not created by swig")
