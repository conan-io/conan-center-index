from conans import ConanFile, CMake, tools
import os

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["PAHO_MQTT_C_ASYNC"] = self.options["paho-mqtt-c"].asynchronous
        cmake.definitions["PAHO_MQTT_C_SHARED"] = self.options["paho-mqtt-c"].shared
        cmake.definitions["PAHO_MQTT_C_WITH_SSL"] = self.options["paho-mqtt-c"].ssl
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)

