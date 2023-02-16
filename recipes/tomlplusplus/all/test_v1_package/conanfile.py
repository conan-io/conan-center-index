from conans import ConanFile, CMake
from conan.tools.scm import Version
from conan.tools.build import cross_building
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        if Version(self.deps_cpp_info["tomlplusplus"].version) < "1.3.0":
            self.single_header_only = True
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "8":
            self.single_header_only = True
        if hasattr(self, "single_header_only"):
            cmake.definitions["TOMLPP_BUILD_SINGLE_ONLY"] = True
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            conf_path = os.path.join(self.recipe_folder, "..", "test_package", "configuration.toml")
            self.run(f"{bin_path} {conf_path}", run_environment=True)
            if not hasattr(self, "single_header_only"):
                bin_path = os.path.join("bin", "test_package_multi")
                self.run(f"{bin_path} {conf_path}", run_environment=True)
