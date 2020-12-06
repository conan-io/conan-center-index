from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        self.run("eu-ar --version", run_environment=True)
        
        bin_path = os.path.join("bin", "test_package")
        archive_path = "archive.a"

        self.run("eu-ar r {0} {1}".format(archive_path, bin_path), run_environment=True)
        self.run("eu-objdump -d {0}".format(bin_path), run_environment=True)
        if not tools.cross_building(self.settings):            
            self.run("{} {}".format(bin_path, bin_path), run_environment=True)

            self.run("{} {}".format(bin_path, archive_path), run_environment=True)
