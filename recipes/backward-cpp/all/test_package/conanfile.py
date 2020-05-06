from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        compiler = self.settings.compiler
        if compiler == 'Visual Studio':
            runtime = str(self.settings.compiler.runtime)
            cmake.definitions["MSVC_RUNTIME_TYPE"] = '/' + runtime
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join(self.build_folder, "test_package")
            self.run(bin_path, run_environment=True)
