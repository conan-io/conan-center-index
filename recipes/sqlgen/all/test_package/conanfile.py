from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.dependencies[self.tested_reference_str].options.with_mysql:
            tc.preprocessor_definitions["TEST_MYSQL_ENABLED"] = True

        if self.dependencies[self.tested_reference_str].options.with_postgres:
            tc.preprocessor_definitions["TEST_POSTGRES_ENABLED"] = True

        if self.dependencies[self.tested_reference_str].options.with_sqlite3:
            tc.preprocessor_definitions["TEST_SQLITE3_ENABLED"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
