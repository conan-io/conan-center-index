from conans import ConanFile, tools


class DefaultNameConan(ConanFile):
    settings = "os"

    def build(self):
        pass

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("perl -S mpc.pl --version", run_environment=True)
