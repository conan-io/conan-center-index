# -*- coding: utf-8 -*-
import os
from conans import ConanFile


class DefaultNameConan(ConanFile):
    settings = "os", "arch"

    def test(self):
        self.run("nasm --version", run_environment=True)
        if self.settings.os == "Linux" and self.settings.arch == "x86_64":
            asm_file = os.path.join(self.source_folder, "hello_linux.asm")
            out_file = os.path.join(self.build_folder, "hello_linux.o")
            bin_file = os.path.join(self.build_folder, "hello_linux")
            self.run("nasm -felf64 {} -o {}".format(asm_file, out_file), run_environment=True)
            self.run("ld hello_linux.o -o {}".format(bin_file), run_environment=True)
            self.run(bin_file)
