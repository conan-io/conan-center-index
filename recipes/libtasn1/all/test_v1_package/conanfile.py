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
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            asn = os.path.join(self.source_folder, os.pardir, "test_package", "pkix.asn")
            self.run(f"{bin_path} {asn}", run_environment=True)
