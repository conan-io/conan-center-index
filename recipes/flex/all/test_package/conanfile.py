import os
from conans import ConanFile, CMake, tools

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        self.run("flex -+ --outfile basic_nr.cpp %s" % os.path.join(self.source_folder, "basic_nr.l"), run_environment=True)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings, skip_x64_x86=True):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
            
            self.run("flex --version", run_environment=True)
