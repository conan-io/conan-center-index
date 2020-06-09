import os

from conans import ConanFile, CMake, tools


class QuickfixTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    options = {"ssl": [True, False], "fPIC": [True, False]}
    default_options = "ssl=False", "fPIC=True"
    generators = "cmake"

    def configure(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
        else:
            self.options["quickfix"].fPIC = self.options.fPIC

        self.options["quickfix"].ssl = self.options.ssl

    def build(self):
        self.source()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            program = "executor"

            self.run(f".{os.sep}{program}", run_environment=True,
                     cwd=f"{self.build_folder}{os.sep}bin")
