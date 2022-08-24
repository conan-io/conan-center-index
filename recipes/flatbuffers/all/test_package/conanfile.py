from conan import ConanFile, tools
from conans import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build_requirements(self):
        if hasattr(self, "settings_build") and tools.cross_building(self) and \
           not self.options["flatbuffers"].header_only: # due to missing package id of build requirement if header_only
            self.build_requires(str(self.requires["flatbuffers"]))

    def build(self):
        cmake = CMake(self)
        cmake.definitions["FLATBUFFERS_HEADER_ONLY"] = self.options["flatbuffers"].header_only
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.run(os.path.join("bin", "test_package"), run_environment=True)
            self.run(os.path.join("bin", "sample_binary"), run_environment=True)
