from conans import ConanFile, CMake, tools
import os


class DefaultNameConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        imgfile = os.path.join(self.source_folder, 'comp_short_decode_piz.exr')
        with tools.chdir('bin'):
            self.run(".%stestPackage %s" % (os.sep, imgfile), run_environment=True)
