import os
from conans import ConanFile, tools, CMake


class TestPackgeConan(ConanFile):
    settings = "os", "arch"
    test_type = "build_requires"
    generators = "cmake"

    def build(self):
        # It only makes sense to build a library, if the target os is Android
        if self.settings.os == "Android":
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self):
            if self.settings.os == "Windows":
                self.run("ndk-build.cmd --version", run_environment=True)
            else:
                self.run("ndk-build --version", run_environment=True)

        # Run the project that was built using Android NDK
        if self.settings.os == "Android":
            test_file = os.path.join("bin", "test_package")
            assert os.path.exists(test_file)
            # self.run("android-emulator {}".format(test_file), run_environment=True)
