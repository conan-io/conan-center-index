from conans.model.conan_file import ConanFile
from conans import CMake, tools
import os


class DefaultNameConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def imports(self):
        self.copy(pattern="*.dll", dst="bin", src="bin")
        self.copy(pattern="*.dylib", dst="bin", src="lib")

    def test(self):
        imgfile = os.path.join(self.source_folder, 'comp_short_decode_piz.exr')
        with tools.chdir('bin'):
            self.run(".%stestPackage %s" % (os.sep, imgfile), run_environment=True)
