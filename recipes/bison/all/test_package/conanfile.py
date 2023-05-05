from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.microsoft import unix_path
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "VirtualBuildEnv", "VirtualRunEnv"
    test_type = "explicit"
    win_bash = True

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def layout(self):
        cmake_layout(self)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
        if self._settings_build.os == "Windows":
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @property
    def _mc_parser_source(self):
        return os.path.join(self.source_folder, "mc_parser.yy")

    def test(self):
        self.run("bison --version")
        self.run("yacc --version")
        self.run(f"bison -d {unix_path(self, self._mc_parser_source)}")
