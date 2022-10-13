from conan import ConanFile
from conan.tools.build import cross_building
from conans import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build_requirements(self):
        if hasattr(self, "settings_build") and cross_building(self):
            self.build_requires(str(self.requires["protobuf"]))

    def build(self):
        cmake = CMake(self)
        cmake.definitions["protobuf_LITE"] = self.options["protobuf"].lite
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            self.run("protoc --version", run_environment=True)
            self.run(os.path.join("bin", "test_package"), run_environment=True)
