from conans import ConanFile


class TestPackageConan(ConanFile):

    def test(self):
        self.run("cppcheck --version", run_environment=True)
        self.run("cppcheck --enable=warning,style,performance --std=c++11 ./main.cpp",
                 cwd=self.source_folder, run_environment=True)
