from conans import ConanFile


class TestPackageConan(ConanFile):
    settings = "os", "arch"
    generators = "txt"

    def test(self):
        for exe in ['gettext', 'ngettext', 'msgcat', 'msgmerge']:
            self.run("%s --version" % exe, run_environment=True)
