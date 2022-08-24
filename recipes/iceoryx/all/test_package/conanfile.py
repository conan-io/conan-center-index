import os
from conan import ConanFile
from conans import CMake

class IceoryxTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = ["cmake", "cmake_find_package_multi"]

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        # ToDo : add an executable which can be
        # executed in container.
        # currently seems shared memory in container is
        # a bad idea (checked on 3 different linux devices
        # always ok - but in container get
        # "fatal SIGBUS signal appeared caused by memset")
        path, dirs, files = next(os.walk("bin"))
        print("All %d example files are present" % (len(files)))
