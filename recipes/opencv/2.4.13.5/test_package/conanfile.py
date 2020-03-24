from conans import ConanFile, CMake
import os
import platform


class OpenCVTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def imports(self):
        self.copy("*.dll", "bin", "bin")
        self.copy("*.dylib", "bin", "lib")
        self.copy("haarcascade*.xml", "bin", "data")

    def test(self):
        ext = ".exe" if platform.system() == "Windows" else ""
        assert (os.path.exists("bin/lena%s" % ext))
