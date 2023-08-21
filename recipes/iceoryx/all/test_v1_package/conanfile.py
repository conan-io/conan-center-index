import os
import os.path
from conans import ConanFile, CMake

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
        bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
        os.path.isfile(bin_path)
        if can_run(self):
            self.run(bin_path, env="conanrun")
