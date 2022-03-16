import os
from conans import ConanFile, CMake

class IceoryxTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = ["cmake", "cmake_find_package_multi"]
    requires = ["cmake/3.16.2"]

    def build(self):
        cmake = CMake(self)
        if not self.deps_cpp_info["iceoryx"].version.startswith("1.0"):
            cmake.definitions["USE_HOOFS"] = True 
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
