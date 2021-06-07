from conans import ConanFile, CMake, tools
from conans.errors import ConanException
import os
import sys


class MocTestConan(ConanFile):
    _versionToTest = '0.9.302' # CHECKRECIPE REPLACE ME
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def requirements(self):
        self.requires('moc/' + self._versionToTest)

    def build(self):
        if not tools.cross_building(self.settings, skip_x64_x86=True):
            print("Testing version of moc");
            try:
                self.run("moc -v", run_environment=True)
            except ConanException as err:
                print("MOC failed to run with err %s" % err );
                raise
            except:
                print("MOC failed to run", sys.exc_info()[0]);
                raise

            moc_bin = tools.which("moc")
            print("Moc was located at '%s'" % moc_bin);
            if not moc_bin.startswith(self.deps_cpp_info["moc"].rootpath):
                raise ConanException("Wrong moc executable captured")
            cmake = CMake(self)
            cmake.definitions["MOC_ROOT"] = self.deps_cpp_info["moc"].rootpath
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self.settings, skip_x64_x86=True):
            os.chdir("bin")
            self.run(".%stest_package" % os.sep)
