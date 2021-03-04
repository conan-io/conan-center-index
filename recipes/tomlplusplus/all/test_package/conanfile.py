from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        if tools.Version(self.deps_cpp_info["tomlplusplus"].version) < "1.3.0":
            cmake.definitions["TOMLPP_BUILD_SINGLE_ONLY"] = True
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "8":
            cmake.definitions["TOMLPP_BUILD_SINGLE_ONLY"] = True
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
