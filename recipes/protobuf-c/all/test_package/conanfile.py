from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build_requirements(self):
        if tools.cross_building(self.settings):
            self.build_requires(str(self.requires['protobuf']))

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("protoc --version", run_environment=True)
            self.run(os.path.join("bin", "test_package"), run_environment=True)
