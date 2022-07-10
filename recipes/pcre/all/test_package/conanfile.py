from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build_requirements(self):
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            # Workaround for CMake bug with error message:
            # Attempting to use @rpath without CMAKE_SHARED_LIBRARY_RUNTIME_C_FLAG being
            # set. This could be because you are using a Mac OS X version less than 10.5
            # or because CMake's platform configuration is corrupt.
            # FIXME: Remove once CMake on macOS/M1 CI runners is upgraded.
            self.build_requires("cmake/3.22.0")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            bin_path = os.path.join("bin", "test_package")
            arguments = "{}w+ conan-center-index".format("\\" if self.settings.os == "Windows" else "\\\\")
            self.run("{} {}".format(bin_path, arguments), run_environment=True)
