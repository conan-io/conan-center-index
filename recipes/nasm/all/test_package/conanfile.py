from conan import ConanFile
from conan.tools.build import can_run
import os


class TestPackageConan(ConanFile):
    # settings = "os", "arch",
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        if can_run(self):
            self.run("nasm --version", env="conanrun")
            asm_file = os.path.join(self.source_folder, "hello_linux.asm")
            out_file = os.path.join(self.build_folder, "hello_linux.o")
            bin_file = os.path.join(self.build_folder, "hello_linux")
            self.run(f"nasm -felf64 {asm_file} -o {out_file}", env="conanrun")
            if self.settings.os == "Linux" and self.settings.arch == "x86_64":
                # TODO was tools.get_env, what should it be?
                ld = os.getenv("LD", "ld")
                self.run(f"{ld} hello_linux.o -o {bin_file}", env="conanrun")
                self.run(bin_file)
