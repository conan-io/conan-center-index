import os
from conans import ConanFile, tools


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def test(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            self.run("nasm --version", run_environment=True)
            asm_file = os.path.join(self.source_folder, "hello_linux.asm")
            out_file = os.path.join(self.build_folder, "hello_linux.o")
            bin_file = os.path.join(self.build_folder, "hello_linux")
            self.run(f"nasm -felf64 {asm_file} -o {out_file}", run_environment=True)
            if self.settings.os == "Linux" and self.settings.arch == "x86_64":
                ld = tools.get_env("LD", "ld")
                self.run(f"{ld} hello_linux.o -o {bin_file}", run_environment=True)
                self.run(bin_file)
