import os

from conans import ConanFile, CMake, tools


class Chai3dTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        if self.options["chai3d"].with_bullet:
            cmake.definitions["CHAI3D_WITH_BULLET"] = "TRUE"
        if self.options["chai3d"].with_ode:
            cmake.definitions["CHAI3D_WITH_ODE"] = "TRUE"
        if self.options["chai3d"].with_gel:
            cmake.definitions["CHAI3D_WITH_GEL"] = "TRUE"
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            os.chdir("bin")
            self.run(".%stest_chai3d" % os.sep)
            if self.options["chai3d"].with_bullet:
                self.run(".%stest_chai3d-bullet" % os.sep)
            if self.options["chai3d"].with_ode:
                self.run(".%stest_chai3d-ode" % os.sep)
            if self.options["chai3d"].with_gel:
                self.run(".%stest_chai3d-gel" % os.sep)