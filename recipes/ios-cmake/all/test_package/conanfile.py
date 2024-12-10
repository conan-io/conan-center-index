import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def generate(self):
        info = self.dependencies.build["ios-cmake"].conf_info
        cmake_prog = info.get("user.ios-cmake:cmake_program", check_type=str)
        toolchain = info.get("user.ios-cmake:cmake_toolchain_file", check_type=str)
        assert os.path.basename(cmake_prog) == "cmake-wrapper"
        assert os.path.isfile(cmake_prog)
        assert os.path.basename(toolchain) == "ios.toolchain.cmake"
        assert os.path.isfile(toolchain)

    def test(self):
        if can_run(self):
            self.run(f"cmake-wrapper {self.source_folder}")
            self.run("cmake-wrapper --build .")
