from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        self.run("eu-ar --version", run_environment=True)
        bin_path = os.path.join("bin", "test_package")
        archive_path = "archive.a"
        self.run(f"eu-ar r {archive_path} {bin_path}", run_environment=True)
        self.run(f"eu-objdump -d {bin_path}", run_environment=True)
        if not tools.cross_building(self):
            self.run(f"{bin_path} {bin_path}", run_environment=True)
            self.run(f"{bin_path} {archive_path}", run_environment=True)
