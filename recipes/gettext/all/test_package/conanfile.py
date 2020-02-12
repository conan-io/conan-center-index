from conans import ConanFile


class TestPackageConan(ConanFile):
    settings = "os", "arch"
    generators = "txt"

    def test(self):
        self.run("gettext --version", run_environment=True)
        self.run("ngettext --version", run_environment=True)
