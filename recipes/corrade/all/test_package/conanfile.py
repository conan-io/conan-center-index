from conan import ConanFile, tools
from conans import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["WITH_UTILITY"] = self.options["corrade"].with_utility
        if self.deps_cpp_info["corrade"].version == "2019.10":
            cmake.definitions["VERSION_2019_10"] = True
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)

            if self.options["corrade"].with_utility:
                # Run corrade-rc
                self.run("corrade-rc --help", run_environment=True)

        if self.settings.os == "Emscripten":
            bin_path = os.path.join("bin", "test_package.js")
            self.run("node {}".format(bin_path), run_environment=True)
