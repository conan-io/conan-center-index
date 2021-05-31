from conans import ConanFile, CMake, tools
import os

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"
    skip_build = False
    skip_testing = False

    def build(self):
        if self.settings.os == "Windows":
            if (str(self.settings.compiler.runtime).startswith("MT") and self.options['fast-cdr'].shared):
                # This combination leads to an fast-cdr error when linking
                # linking dynamic '*.dll' and static MT runtime
                # see https://github.com/eProsima/Fast-CDR/blob/master/include/fastcdr/eProsima_auto_link.h#L37
                # (2021-05-31)
                self.skip_build = True
                self.skip_testing = True
        if tools.cross_building(self.settings):
            self.skip_testing = True
        if not self.skip_build:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not self.skip_testing:
            bin_path = os.path.join("bin", "test_package_1")
            self.run(bin_path, run_environment=True)
            bin_path = os.path.join("bin", "test_package_2")
            self.run(bin_path, run_environment=True)
