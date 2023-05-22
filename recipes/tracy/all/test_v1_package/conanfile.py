from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def generate(self):
        # test_package might fail in some CI environments without it
        env = tools.env.Environment()
        env.define("TRACY_NO_INVARIANT_CHECK", "1")
        env.vars(self, scope="run").save_script("tracy_avoid_ci_crash")

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
