from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        if self.options["flatbuffers"].flatbuffers:
            cmake = CMake(self)
            cmake.definitions["FLATBUFFERS_HEADER_ONLY"] = self.options["flatbuffers"].header_only
            cmake.definitions["FLATBUFFERS_SHARED"] = not self.options["flatbuffers"].header_only and self.options["flatbuffers"].shared
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            if self.options["flatbuffers"].flatbuffers:
                bin_path = os.path.join("bin", "test_package")
                self.run(bin_path, run_environment=True)
            if self.options["flatbuffers"].flatc:
                self.run("flatc --version", run_environment=True)
