from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    test_type = "explicit"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        self.build_requires(self.tested_reference_str)
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @property
    def _mc_parser_source(self):
        return os.path.join(self.source_folder, os.pardir, "test_package", "mc_parser.yy")

    def test(self):
        self.run("bison --version")
        self.run("yacc --version", win_bash=tools.os_info.is_windows)
        self.run(f"bison -d {self._mc_parser_source}")
