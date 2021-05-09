from conans import CMake, ConanFile, tools

import os


class AngelScriptTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            if self.settings.compiler == "Visual Studio":
                bin_path = self.settings.build_type.value
            else:
                bin_path = "."
            self.run(os.path.join(bin_path, "example"), run_environment=True)
