from conans import ConanFile, CMake, tools
from conans.tools import Version
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["PfrMajorVersion"] = Version(
            self.deps_cpp_info["pfr"].version).major
        # PFR 1.0.4 doesn't support Visual Studio in C++14 mode, requires C++17.
        # Otherwise, at least C++14 is required.
        cmake.definitions["CMAKE_CXX_STANDARD"] = "14" \
            if Version(self.deps_cpp_info["pfr"].version) >= "2.0.0" \
                or self.settings.compiler != "Visual Studio" \
            else "17"
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
