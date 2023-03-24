from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        if hasattr(self, "settings_build"):
            self.build_requires(self.tested_reference_str)

    def build(self):
        with tools.no_op() if hasattr(self, "settings_build") else tools.run_environment(self):
            cmake = CMake(self)
            cmake.definitions["protobuf_LITE"] = self.options["protobuf"].lite
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.run("protoc --version", run_environment=True)
            self.run(os.path.join("bin", "test_package"), run_environment=True)
