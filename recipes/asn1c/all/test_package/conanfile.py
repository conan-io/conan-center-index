from conans import CMake
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.build import cross_building
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    generators = "cmake"

    def build_requirements(self):
        self.tool_requires(str(self.requires["asn1c"]))

    def build(self):
        copy(self, "MyModule.asn1", src=self.source_folder, dst=self.build_folder)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
