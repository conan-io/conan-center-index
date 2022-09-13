from conan import ConanFile
from conan.tools.cmake import cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def test(self):
        self.run("jwasm -h", ignore_errors=True)
        obj_file = os.path.join(self.build_folder, "Lin64_1.o")
        asm_file = os.path.join(self.source_folder, "Lin64_1.asm") # content from https://www.japheth.de/JWasm/Lin64_1.html
        self.run(f"jwasm -elf64 -Fo={obj_file} {asm_file}")
        if self._settings_build.os == "Linux" and self._settings_build.arch == "x86_64":
            bin_file = os.path.join(self.build_folder, "Lin64_1")
            self.run(f"ld {obj_file} -o {bin_file}")
            self.run(bin_file, ignore_errors=True)
