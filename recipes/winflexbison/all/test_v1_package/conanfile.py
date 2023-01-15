from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    test_type = "explicit"

    def build_requirements(self):
        self.build_requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        self.run("win_flex --version")
        self.run("win_bison --version")
        if not tools.cross_building(self, skip_x64_x86=True):
            bison_test = os.path.join("bin", "bison_test_package")
            self.run(bison_test, run_environment=True)
            flex_test = os.path.join("bin", "flex_test_package")
            basic_nr_txt = os.path.join(self.source_folder, os.pardir, "test_package", "basic_nr.txt")
            self.run(f"{flex_test} {basic_nr_txt}", run_environment=True)
