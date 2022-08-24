from conan import ConanFile, tools
from conans import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def requirements(self):
        self.requires("nlohmann_json/3.9.1")
        self.requires("rapidjson/cci.20200410")
        self.requires("picojson/1.3.0")

    def test(self):
        if not tools.build.cross_building(self, self.settings):
            bin_path = os.path.join("bin", "test_package")
            schema_file = os.path.abspath(os.path.join(self.source_folder, "schema.json"))
            valid_file = os.path.abspath(os.path.join(self.source_folder, "valid.json"))
            invalid_file = os.path.abspath(os.path.join(self.source_folder, "invalid.json"))
            self.run(
                "{} {} {} {}".format(bin_path, schema_file, valid_file, invalid_file),
                run_environment=True
            )
