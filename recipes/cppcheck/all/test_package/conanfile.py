from conan import ConanFile


class TestPackageConan(ConanFile):
    settings = "os", "arch"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def test(self):
        if not cross_building(self):
            self.run("cppcheck --enable=warning,style,performance --std=c++11 .",
                     cwd=self.source_folder, env="conanbuild")
            if self.settings.os == 'Windows':
                # Unable to work with Environment variable CPPCHECK_HTML_REPORT
                #elf.run(f"{sys.executable} %CPPCHECK_HTML_REPORT% -h", run_environment=True)
                pass
            else:
                self.run("cppcheck-htmlreport -h", run_environment=True)
