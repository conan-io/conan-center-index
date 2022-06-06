import os
from conans import ConanFile, CMake


class TestPackgeConan(ConanFile):
    settings = "os", "arch"
    test_type = "explicit"
    generators = "cmake"

    def build_requirements(self):
        self.build_requires(self.tested_reference_str)

    def build(self):
        # It only makes sense to build a library, if the target os is Linux
        if self.settings.os == "Linux":
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        # Run the project that was built using the SDK
        if self.settings.os == "Linux":
            test_file = os.path.join("bin", "test_package")
            assert os.path.exists(test_file)
