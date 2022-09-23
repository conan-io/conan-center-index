from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"

    def build(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            with tools.run_environment(self):
                cmake = CMake(self)
                cmake.configure()
                cmake.build()

    def test(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            self.run("win_flex --version", run_environment=True)
            self.run("win_bison --version", run_environment=True)

            bison_test = os.path.join("bin", "bison_test_package")
            self.run(bison_test, run_environment=True)
            flex_test = os.path.join("bin", "flex_test_package")
            basic_nr_txt = os.path.join(self.source_folder, os.pardir, "test_package", "basic_nr.txt")
            self.run(f"{flex_test} {basic_nr_txt}", run_environment=True)
