import shutil,os
from conans import ConanFile, CMake, tools

class TestOpenE57Conan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        if not tools.cross_building(self):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path=""
            if self.settings.compiler == "Visual Studio":
                bin_path = os.path.join("bin", "{}".format(self.settings.build_type), "openE57_example")
            else:
                bin_path = os.path.join("bin", "openE57_example")
            self.run(bin_path, run_environment=True)
