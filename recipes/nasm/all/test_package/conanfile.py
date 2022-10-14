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
            self.run("nasm -felf64 {} -o {}".format(asm_file, out_file), env="conanrun")
            if self.settings.os == "Linux" and self.settings.arch == "x86_64":
                ld = tools.get_env("LD", "ld")
                self.run("{} hello_linux.o -o {}".format(ld, bin_file), env="conanrun")
                self.run(bin_file)
