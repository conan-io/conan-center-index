from conans import ConanFile, CMake
import os

username = os.getenv("CONAN_USERNAME", "jjkoshy")
channel = os.getenv("CONAN_CHANNEL", "stable")

class LevelDBTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    requires = "leveldb/1.22@%s/%s" % (username, channel)
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        os.chdir("bin")
        self.run("LD_LIBRARY_PATH=$(pwd) && .%sexample" % os.sep)
