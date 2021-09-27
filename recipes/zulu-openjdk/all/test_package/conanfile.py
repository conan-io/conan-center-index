from conans import ConanFile, tools
from six import StringIO


class TestPackage(ConanFile):

    def build(self):
        pass # nothing to build, but tests should not warn

    def test(self):
        test_cmd = ['java', '--version']
        output = StringIO()
        if tools.cross_building(self):
            self.run("java --version", run_environment=True)
        else:
            self.run(test_cmd, output=output)
        version_info = output.getvalue()
        if "Zulu" in version_info:
            pass
        else:
            raise Exception("java call seems not use the Zulu bin")
