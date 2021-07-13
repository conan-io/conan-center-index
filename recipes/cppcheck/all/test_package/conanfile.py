from conans import ConanFile, tools


class TestPackageConan(ConanFile):
    settings = "os", "arch"

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("cppcheck --version", run_environment=True)
            self.run("cppcheck --enable=warning,style,performance --std=c++11 ./main.cpp",
                     cwd=self.source_folder, run_environment=True)
