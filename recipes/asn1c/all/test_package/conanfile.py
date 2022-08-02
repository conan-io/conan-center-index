from conans import ConanFile, CMake, tools
import os, shutil


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    generators = "cmake"

    def build_requirements(self):
        self.build_requires(str(self.requires["asn1c"]))

    def build(self):
        shutil.copy(os.path.join(self.source_folder, "MyModule.asn1"), self.build_folder)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
