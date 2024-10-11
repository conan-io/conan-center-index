from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["WITH_SHORTHAND"] = self.options["snitch"].with_shorthand_macros
        cmake.definitions["HEADER_ONLY"] = self.options["snitch"].header_only
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.run(os.path.join("bin", "standalone"), run_environment=True)
