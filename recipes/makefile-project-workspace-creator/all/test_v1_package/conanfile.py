from conans import ConanFile, tools


class DefaultNameConan(ConanFile):
    settings = "os"

    def build(self):
        pass

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.tool_requires("strawberryperl/5.32.1.1")

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("perl -S mpc.pl --version", run_environment=True)
