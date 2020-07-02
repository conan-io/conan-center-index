from conans import ConanFile


class DefaultNameConan(ConanFile):
    settings = "os"

    def build(self):
        pass

    def test(self):
        self.run("perl -S mpc.pl --version", run_environment=True)
