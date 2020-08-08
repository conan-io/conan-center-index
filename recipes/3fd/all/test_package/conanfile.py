from conans import ConanFile, CMake, tools
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        shutil.copy(os.path.join(self.source_folder, "test_package.3fd.config"),
                    os.path.join(self.build_folder, "bin", "test_package.3fd.config"))
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
