import os
import shutil
import re

from conans import ConanFile, CMake, tools


class QuickfixTestConan(ConanFile):
    version = "1.15.1"
    settings = "os", "compiler", "build_type", "arch"
    options = {"ssl": [True, False], "fPIC": [True, False]}
    default_options = "ssl=False", "fPIC=True"
    generators = "cmake"
    file_pattern = re.compile(r'quickfix-(.*)')

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        files = os.listdir()
        quickfix_dir = list(filter(self.file_pattern.search, files))
        shutil.rmtree("source", ignore_errors=True)
        shutil.move(f"{quickfix_dir[0]}{os.sep}examples", f".{os.sep}source{os.sep}examples")

        tools.replace_in_file("source/examples/executor/C++/Application.cpp",
                              "#pragma warning( disable : 4503 4355 4786 )",
                              '''
#pragma warning( disable : 4503 4355 4786 )
#include "config.h"
''')

        tools.replace_in_file("source/examples/executor/C++/executor.cpp",
                              "#pragma warning( disable : 4503 4355 4786 )",
                              '''
#pragma warning( disable : 4503 4355 4786 )
#include "config.h"
''')

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
            if self.settings.os == "Windows":
                program = "executor_cpp"
            else:
                program = "executor"

            self.run(f".{os.sep}{program}", run_environment=True,
                     cwd=f"{self.build_folder}{os.sep}bin")
