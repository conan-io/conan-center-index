from conans import ConanFile, CMake, tools
from conans.errors import ConanException
import os
import sys
from six import StringIO


class MocTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        if not tools.cross_building(self.settings, skip_x64_x86=True):
            moc_bin = tools.which("moc")
            self.output.info("Moc was located at '%s'" % moc_bin);
            if not moc_bin.startswith(self.deps_cpp_info["moc"].rootpath):
                raise ConanException("Wrong moc executable captured")
            versionInfo=""
            try:
                mybuf = StringIO()
                self.run("moc -v", output=mybuf, run_environment=True)
                versionInfo = mybuf.getvalue().rstrip()
                if versionInfo == "":
                    self.output.error("NO OUTPUT FROM MOC")
                else:
                    self.output.info("MOC Version: '%s'" % versionInfo)
            except ConanException as err:
                raise
            except:
                raise ConanException("Moc version not found. Moc may not have been built correctly")

            if not "version" in versionInfo:
                raise ConanException("Moc version not found. Moc may not have been built correctly")
            cppExe = "/usr/lib/cpp"
            cpp_bin = tools.which(cppExe)
            if cpp_bin == None:
                self.output.warn("%s is required by moc, but cpp was not found" % cppExe);
                return

            cmake = CMake(self)
            cmake.definitions["MOC_ROOT"] = self.deps_cpp_info["moc"].rootpath
            cmake.configure()
            cmake.build()

    def test(self):
        cppExe = "/usr/lib/cpp"
        cpp_bin = tools.which(cppExe)
        if cpp_bin == None:
            self.output.warn("%s is required by moc, but cpp was not found" % cppExe);
            return
        if not tools.cross_building(self.settings, skip_x64_x86=True):
            os.chdir("bin")
            self.run(".%stest_package" % os.sep)
