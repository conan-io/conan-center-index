from conans import ConanFile, tools
import os
import shutil


class TestPackageConan(ConanFile):

    exports_sources = "hello.c", "text.s"

    _targets = ("c64", "apple2")

    def build(self):
        for src in self.exports_sources:
            shutil.copy(os.path.join(self.source_folder, src), os.path.join(self.build_folder, src))
        try:
            os.unlink("c64.lib")
        except FileNotFoundError:
            pass
        for target in self._targets:
            tools.mkdir(target)
            try:
                os.unlink("hello_{}".format(target))
            except FileNotFoundError:
                pass
            self.run("{p} -O -t {t} hello.c -o {t}/hello.s".format(p=os.environ["CC65"], t=target))
            self.run("{p} -t {t} {t}/hello.s -o {t}/hello.o".format(p=os.environ["AS65"], t=target))
            self.run("{p} -t {t} text.s -o {t}/text.o".format(p=os.environ["AS65"], t=target))
            self.run("{p} -o hello_{t} -t {t} {t}/hello.o {t}/text.o {t}.lib".format(p=os.environ["LD65"], t=target))

    def test(self):
        for target in self._targets:
            assert os.path.isfile("hello_{}".format(target))
