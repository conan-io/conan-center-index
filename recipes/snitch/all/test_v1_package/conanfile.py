from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        tc.variables["WITH_SHORTHAND"] = self.dependencies[self.tested_reference_str].options.with_shorthand_macros
        tc.variables["HEADER_ONLY"] = self.dependencies[self.tested_reference_str].options.header_only
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.run(os.path.join("bin", "standalone"), run_environment=True)
