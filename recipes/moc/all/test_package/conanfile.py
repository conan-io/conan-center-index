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
            self.output.info("cpp was located at '%s'" % cpp_bin);
            try:
                mybuf = StringIO()
                self.run(cppExe + " -I" + self.source_folder + " " + self.source_folder + "/test_app.moc", output=mybuf, run_environment=True)
                outputText = mybuf.getvalue().rstrip()
                if outputText == "":
                    self.output.error("NO OUTPUT FROM C preprocessor: " + cppExe)
                else:
                    self.output.info(outputText)
            except ConanException as err:
                raise
            except:
                raise ConanException("Error running " + cppExe + ":" +  sys.exc_info()[0])

            cmake = CMake(self)
            cmake.definitions["MOC_ROOT"] = self.deps_cpp_info["moc"].rootpath
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self.settings, skip_x64_x86=True):
            os.chdir("bin")
            self.run(".%stest_package" % os.sep)
