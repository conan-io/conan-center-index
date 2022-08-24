from conan import ConanFile, tools
from conans import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        if tools.Version(self.deps_cpp_info["tomlplusplus"].version) < "1.3.0":
            self.single_header_only = True
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "8":
            self.single_header_only = True
        if hasattr(self, "single_header_only"):
            cmake.definitions["TOMLPP_BUILD_SINGLE_ONLY"] = True
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
            if not hasattr(self, "single_header_only"):
                bin_path_multi = os.path.join("bin", "test_package_multi")
                self.run(bin_path_multi, run_environment=True)
