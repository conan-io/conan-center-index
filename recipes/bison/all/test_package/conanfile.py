from conan import ConanFile, tools
from conan.tools.cmake import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    @property
    def _mc_parser_source(self):
        return os.path.join(self.source_folder, "mc_parser.yy")

    def build(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            # verify bison may run
            self.run("bison --version", run_environment=True)
            # verify yacc may run
            self.run("yacc --version", run_environment=True, win_bash=tools.os_info.is_windows)
            # verify bison may preprocess something
            self.run("bison -d {}".format(self._mc_parser_source), run_environment=True)

            # verify CMake integration
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
