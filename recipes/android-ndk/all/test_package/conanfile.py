import os
from conan import ConanFile
from conans import CMake
from conan.tools.build import cross_building


class TestPackgeConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"
    generators = "cmake"

    def build_requirements(self):
        self.build_requires(self.tested_reference_str)

    def build(self):
        # It only makes sense to build a library, if the target os is Android
        if self.settings.os == "Android":
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not cross_building(self):
            if self.settings.os == "Windows":
                self.run("ndk-build.cmd --version", run_environment=True)
            else:
                self.run("ndk-build --version", run_environment=True)

        # Run the project that was built using Android NDK
        if self.settings.os == "Android":
            test_file = os.path.join("bin", "test_package")
            assert os.path.exists(test_file)
