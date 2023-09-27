from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
import os

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires("nlohmann_json/3.11.2")
        self.requires("rapidjson/cci.20200410")
        self.requires("picojson/1.3.0")
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            schema_file = os.path.join(self.source_folder, "schema.json")
            valid_file = os.path.join(self.source_folder, "valid.json")
            invalid_file = os.path.join(self.source_folder, "invalid.json")
            self.run(f"{bin_path} {schema_file} {valid_file} {invalid_file}", env="conanrun")
