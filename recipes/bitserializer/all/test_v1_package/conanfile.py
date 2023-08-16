from conans import ConanFile, CMake, tools
from conans.errors import ConanException
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def _bitserializer_option(self, name, default=None):
        try:
            return getattr(self.options["bitserializer"], name, default)
        except (AttributeError, ConanException):
            return default

    def build(self):
        cmake = CMake(self)
        cmake.definitions["WITH_CPPRESTSDK"] = self.options["bitserializer"].with_cpprestsdk
        cmake.definitions["WITH_RAPIDJSON"] = self.options["bitserializer"].with_rapidjson
        cmake.definitions["WITH_PUGIXML"] = self.options["bitserializer"].with_pugixml
        cmake.definitions["WITH_RAPIDYAML"] = self._bitserializer_option("with_rapidyaml", False)
        cmake.definitions["WITH_CSV"] = self._bitserializer_option("with_csv", False)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
