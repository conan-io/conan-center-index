from conans import ConanFile, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch"

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("jwasm -h", run_environment=True, ignore_errors=True)
            if self.settings.os == "Linux" and self.settings.arch == "x86_64":
                asm_file = os.path.join(self.source_folder, "Lin64_1.asm") # content from https://www.japheth.de/JWasm/Lin64_1.html
                obj_file = os.path.join(self.build_folder, "Lin64_1.o")
                bin_file = os.path.join(self.build_folder, "Lin64_1")
                self.run("jwasm -elf64 -Fo={obj} {asm}".format(asm=asm_file, obj=obj_file), run_environment=True)
                self.run("ld {obj} -o {bin}".format(obj=obj_file, bin=bin_file))
                self.run(bin_file, ignore_errors=True)
