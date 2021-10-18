from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["WITH_CPPRESTSDK"] = self.options["bitserializer"].with_cpprestsdk
        cmake.definitions["WITH_RAPIDJSON"] = self.options["bitserializer"].with_rapidjson
        cmake.definitions["WITH_PUGIXML"] = self.options["bitserializer"].with_pugixml
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
