from conans import ConanFile, CMake
from conan.tools.build import cross_building
import os


# legacy validation with Conan 1.x
class TestPackageV1Conan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["PAHO_MQTT_CPP_SHARED"] = self.options["paho-mqtt-cpp"].shared
        cmake.definitions["TEST_SSL_OPTION"] = self.options["paho-mqtt-cpp"].ssl
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
