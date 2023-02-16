from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def requirements(self):
        self.requires("nlohmann_json/3.9.1")
        self.requires("rapidjson/cci.20200410")
        self.requires("picojson/1.3.0")

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            schema_file = os.path.abspath(os.path.join(self.source_folder, os.pardir, "test_package", "schema.json"))
            valid_file = os.path.abspath(os.path.join(self.source_folder, os.pardir, "test_package", "valid.json"))
            invalid_file = os.path.abspath(os.path.join(self.source_folder, os.pardir, "test_package", "invalid.json"))
            self.run(
                "{} {} {} {}".format(bin_path, schema_file, valid_file, invalid_file),
                run_environment=True
            )
