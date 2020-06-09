from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["TEST_ENABLE_PUBSUB_CUSTOM_PUBLISH_HANDLING"] = self.options["open62541"].enable_pubsub_custom_publish_handling
        cmake.verbose= True
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            client_bin_path = os.path.join("bin", "test_package_client")
            self.run(client_bin_path, run_environment=True)

            server_bin_path = os.path.join("bin", "test_package_server")
            self.run(server_bin_path, run_environment=True)
