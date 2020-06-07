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
        if not tools.cross_building(self.settings):
            client_bin_path = os.path.join("bin", "test_package_client")
            self.run(client_bin_path, run_environment=True)

            server_bin_path = os.path.join("bin", "test_package_server")
            self.run(server_bin_path, run_environment=True)
