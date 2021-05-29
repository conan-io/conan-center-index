from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build_requirements(self):
        if tools.cross_building(self.settings):
            self.build_requires(str(self.requires['protobuf']))
            
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join(".", "bin", "greeter_client_server")
            self.run(bin_path, run_environment=True)
