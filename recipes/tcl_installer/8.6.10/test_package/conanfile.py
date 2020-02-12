import os

from conans import ConanFile, tools


class TclTestConan(ConanFile):

    def test(self):
        self.run("{} {}".format(os.environ["TCLSH"], os.path.join(self.source_folder, "hello.tcl")), run_environment=True)
