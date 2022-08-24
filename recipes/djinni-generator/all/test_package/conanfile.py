
from io import StringIO
from conans import ConanFile, tools

class TestPackageConan(ConanFile):
    settings = "os", "arch"

    def build(self):
        pass # please no warning that we build nothing

    def test(self):
        if not tools.build.cross_building(self, self.settings):
            output = StringIO()
            self.run("djinni --help", output=output, run_environment=True)
            output.seek(0, 0)
            found_usage = False
            for line in output:
                if "Usage: djinni [options]" in line:
                    found_usage = True
                    break
            assert(found_usage)
