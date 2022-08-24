from conans import ConanFile, tools
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    exports_sources = "hello.c", "text.s"

    _targets = ("c64", "apple2")

    def build(self):
        if not tools.build.cross_building(self, self.settings):
            for src in self.exports_sources:
                shutil.copy(os.path.join(self.source_folder, src), os.path.join(self.build_folder, src))
            for target in self._targets:
                output = "hello_{}".format(target)
                tools.files.mkdir(self, target)
                try:
                    # Try removing the output file to give confidence it is created by cc65
                    os.unlink(output)
                except FileNotFoundError:
                    pass
                self.run("{p} -O -t {t} hello.c -o {t}/hello.s".format(p=os.environ["CC65"], t=target))
                self.run("{p} -t {t} {t}/hello.s -o {t}/hello.o".format(p=os.environ["AS65"], t=target))
                self.run("{p} -t {t} text.s -o {t}/text.o".format(p=os.environ["AS65"], t=target))
                self.run("{p} -o {o} -t {t} {t}/hello.o {t}/text.o {t}.lib".format(o=output, p=os.environ["LD65"], t=target))

    def test(self):
        if not tools.build.cross_building(self, self.settings):
            for target in self._targets:
                assert os.path.isfile("hello_{}".format(target))
